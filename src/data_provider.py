import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import time

class DataProvider:
    """Handles data fetching and management for multiple symbols"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.data_cache = {}
        self.last_update = {}
        self.logger = logging.getLogger(__name__)
        
    def fetch_data(self, symbol: str, period: str = "1d", interval: str = "5m") -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a specific symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                self.logger.warning(f"No data received for {symbol}")
                return None
                
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_columns):
                self.logger.error(f"Missing required columns for {symbol}")
                return None
                
            # Clean data
            data = data.dropna()
            
            # Add some basic validation
            if len(data) < 10:
                self.logger.warning(f"Insufficient data for {symbol}: {len(data)} bars")
                return None
                
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_multi_timeframe_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get data for multiple timeframes for a symbol"""
        timeframes = {
            '5m': self.fetch_data(symbol, period="1d", interval="5m"),
            '15m': self.fetch_data(symbol, period="2d", interval="15m")
        }
        
        # Filter out None values
        return {tf: data for tf, data in timeframes.items() if data is not None}
    
    def update_cache(self):
        """Update data cache for all symbols"""
        self.logger.info("Updating data cache for all symbols...")
        for symbol in self.symbols:
            try:
                self.data_cache[symbol] = self.get_multi_timeframe_data(symbol)
                self.last_update[symbol] = datetime.now()
                time.sleep(0.1)  # Small delay to avoid rate limiting
            except Exception as e:
                self.logger.error(f"Error updating cache for {symbol}: {str(e)}")
        
        self.logger.info(f"Cache updated for {len(self.data_cache)} symbols")
            
    def get_cached_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached data for symbol and timeframe"""
        if symbol in self.data_cache and timeframe in self.data_cache[symbol]:
            return self.data_cache[symbol][timeframe]
        return None
    
    def is_cache_stale(self, symbol: str, max_age_minutes: int = 5) -> bool:
        """Check if cached data is stale"""
        if symbol not in self.last_update:
            return True
        
        time_diff = datetime.now() - self.last_update[symbol]
        return time_diff.total_seconds() > (max_age_minutes * 60)
    
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
