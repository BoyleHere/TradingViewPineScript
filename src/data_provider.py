import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class DataProvider:
    """Enhanced data provider with smart caching and faster updates"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.data_cache = {}
        self.last_update = {}
        self.logger = logging.getLogger(__name__)
        self.cache_timeout = 30  # Reduced from 300 seconds
        self.max_workers = 5  # Concurrent downloads
        self.fast_update_mode = True
        
    def fetch_data(self, symbol: str, period: str = "1d", interval: str = "5m") -> Optional[pd.DataFrame]:
        """Fetch OHLCV data with enhanced error handling and retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(symbol)
                
                # Use shorter periods for faster updates
                if self.fast_update_mode:
                    if interval == "5m":
                        period = "1d"  # Get last day only
                    elif interval == "15m":
                        period = "5d"  # Get last 5 days
                
                data = ticker.history(period=period, interval=interval, prepost=True)
                
                if data.empty:
                    self.logger.warning(f"No data received for {symbol} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Brief pause before retry
                    continue
                    
                # Ensure we have the required columns
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in data.columns for col in required_columns):
                    self.logger.error(f"Missing required columns for {symbol}")
                    continue
                    
                # Clean data and add real-time indicators
                data = data.dropna()
                data['Symbol'] = symbol
                data['LastUpdate'] = datetime.now()
                
                # Add some basic validation
                if len(data) < 10:
                    self.logger.warning(f"Insufficient data for {symbol}: {len(data)} bars")
                    continue
                    
                self.logger.debug(f"Successfully fetched {len(data)} bars for {symbol}")
                return data
                
            except Exception as e:
                self.logger.error(f"Error fetching data for {symbol} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Longer pause for errors
                
        return None
    
    def get_multi_timeframe_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get data for multiple timeframes with concurrent fetching"""
        timeframes = {}
        
        # Use ThreadPoolExecutor for concurrent data fetching
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_timeframe = {
                executor.submit(self.fetch_data, symbol, "1d", "5m"): '5m',
                executor.submit(self.fetch_data, symbol, "5d", "15m"): '15m'
            }
            
            for future in as_completed(future_to_timeframe):
                timeframe = future_to_timeframe[future]
                try:
                    data = future.result()
                    if data is not None:
                        timeframes[timeframe] = data
                except Exception as e:
                    self.logger.error(f"Error fetching {timeframe} data for {symbol}: {str(e)}")
        
        return timeframes
    
    def update_cache(self):
        """Enhanced cache update with concurrent processing"""
        self.logger.info("Updating data cache for all symbols...")
        start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent symbol processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.get_multi_timeframe_data, symbol): symbol 
                for symbol in self.symbols
            }
            
            successful_updates = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    timeframe_data = future.result()
                    if timeframe_data:
                        self.data_cache[symbol] = timeframe_data
                        self.last_update[symbol] = datetime.now()
                        successful_updates += 1
                    else:
                        self.logger.warning(f"No data retrieved for {symbol}")
                except Exception as e:
                    self.logger.error(f"Error updating cache for {symbol}: {str(e)}")
        
        duration = time.time() - start_time
        self.logger.info(f"Cache updated for {successful_updates}/{len(self.symbols)} symbols in {duration:.2f}s")
        
        return successful_updates
            
    def get_cached_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached data for symbol and timeframe"""
        if symbol in self.data_cache and timeframe in self.data_cache[symbol]:
            return self.data_cache[symbol][timeframe]
        return None
    
    def is_cache_stale(self, symbol: str, max_age_seconds: int = None) -> bool:
        """Check if cached data is stale with configurable timeout"""
        if max_age_seconds is None:
            max_age_seconds = self.cache_timeout
            
        if symbol not in self.last_update:
            return True
        
        time_diff = datetime.now() - self.last_update[symbol]
        return time_diff.total_seconds() > max_age_seconds
    
    def get_data_freshness(self, symbol: str) -> str:
        """Get human-readable data freshness indicator"""
        if symbol not in self.last_update:
            return "Never updated"
        
        time_diff = datetime.now() - self.last_update[symbol]
        seconds = int(time_diff.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds//60}m ago"
        else:
            return f"{seconds//3600}h ago"
    
    def force_update_symbol(self, symbol: str) -> bool:
        """Force update a specific symbol's data"""
        try:
            self.data_cache[symbol] = self.get_multi_timeframe_data(symbol)
            self.last_update[symbol] = datetime.now()
            return True
        except Exception as e:
            self.logger.error(f"Error force updating {symbol}: {str(e)}")
            return False
    
    def get_data_status(self) -> Dict[str, Dict]:
        """Get status of cached data"""
        status = {}
        for symbol in self.symbols:
            if symbol in self.data_cache:
                symbol_status = {
                    'last_update': self.last_update.get(symbol, 'Never'),
                    'timeframes': list(self.data_cache[symbol].keys()),
                    'data_points': {tf: len(data) for tf, data in self.data_cache[symbol].items()}
                }
            else:
                symbol_status = {
                    'last_update': 'Never',
                    'timeframes': [],
                    'data_points': {}
                }
            status[symbol] = symbol_status
        
        return status
