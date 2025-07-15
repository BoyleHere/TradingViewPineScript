import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import time

class FVGDetector:
    """Detects Fair Value Gaps and Inversion Fair Value Gaps"""
    
    def __init__(self, threshold: float = 0.001):
        self.threshold = threshold
        self.logger = logging.getLogger(__name__)
        
    def detect_fvg(self, data: pd.DataFrame) -> List[Dict]:
        """
        Detect Fair Value Gaps (FVG)
        
        Bullish FVG: Current candle's low > Two candles ago high (gap up)
        Bearish FVG: Current candle's high < Two candles ago low (gap down)
        
        The middle candle acts as the "imbalance" candle
        """
        fvgs = []
        
        if len(data) < 3:
            return fvgs
            
        for i in range(2, len(data)):
            current = data.iloc[i]
            middle = data.iloc[i-1]
            before = data.iloc[i-2]
            
            # Bullish FVG detection
            # Check if there's a gap between before candle's high and current candle's low
            if (before['High'] < current['Low'] and 
                abs(before['High'] - current['Low']) / current['Low'] > self.threshold):
                
                gap_size = current['Low'] - before['High']
                gap_percentage = (gap_size / before['High']) * 100
                
                fvg = {
                    'type': 'FVG',
                    'direction': 'Bullish',
                    'timestamp': current.name,
                    'gap_start': before['High'],
                    'gap_end': current['Low'],
                    'gap_size': gap_size,
                    'gap_percentage': gap_percentage,
                    'imbalance_candle': middle.name,
                    'price_at_detection': current['Close'],
                    'volume': current['Volume']
                }
                fvgs.append(fvg)
                self.logger.debug(f"Bullish FVG detected at {current.name}: {gap_percentage:.2f}%")
            
            # Bearish FVG detection
            # Check if there's a gap between before candle's low and current candle's high
            elif (before['Low'] > current['High'] and 
                  abs(before['Low'] - current['High']) / current['High'] > self.threshold):
                
                gap_size = before['Low'] - current['High']
                gap_percentage = (gap_size / current['High']) * 100
                
                fvg = {
                    'type': 'FVG',
                    'direction': 'Bearish',
                    'timestamp': current.name,
                    'gap_start': before['Low'],
                    'gap_end': current['High'],
                    'gap_size': gap_size,
                    'gap_percentage': gap_percentage,
                    'imbalance_candle': middle.name,
                    'price_at_detection': current['Close'],
                    'volume': current['Volume']
                }
                fvgs.append(fvg)
                self.logger.debug(f"Bearish FVG detected at {current.name}: {gap_percentage:.2f}%")
                
        return fvgs
    
    def detect_ifvg(self, data: pd.DataFrame, fvgs: List[Dict]) -> List[Dict]:
        """
        Detect Inversion Fair Value Gaps (iFVG)
        
        iFVG occurs when price returns to fill a previously identified FVG
        and then reverses direction, creating an inversion pattern
        """
        ifvgs = []
        
        if not fvgs:
            return ifvgs
            
        for fvg in fvgs:
            fvg_timestamp = fvg['timestamp']
            gap_start = fvg['gap_start']
            gap_end = fvg['gap_end']
            
            # Look for price action after the FVG
            try:
                fvg_index = data.index.get_loc(fvg_timestamp)
                subsequent_data = data.iloc[fvg_index + 1:]
                
                if len(subsequent_data) < 2:
                    continue
                
                for i, (timestamp, row) in enumerate(subsequent_data.iterrows()):
                    if fvg['direction'] == 'Bullish':
                        # Check if price came back down to fill the gap
                        if row['Low'] <= gap_start:
                            # Look for reversal after fill
                            remaining_data = subsequent_data.iloc[i+1:]
                            if len(remaining_data) > 0:
                                # Check for bullish reversal after fill
                                reversal_found = False
                                for j, (rev_timestamp, rev_row) in enumerate(remaining_data.iterrows()):
                                    if rev_row['High'] > gap_end:  # Price moved back above gap
                                        reversal_found = True
                                        break
                                    if j >= 5:  # Limit search to next 5 candles
                                        break
                                
                                if reversal_found:
                                    ifvg = {
                                        'type': 'iFVG',
                                        'direction': 'Bullish',
                                        'timestamp': timestamp,
                                        'original_fvg': fvg,
                                        'fill_price': row['Low'],
                                        'fill_percentage': ((gap_start - row['Low']) / gap_start) * 100,
                                        'reversal_confirmed': True,
                                        'volume': row['Volume']
                                    }
                                    ifvgs.append(ifvg)
                                    self.logger.debug(f"Bullish iFVG detected at {timestamp}")
                            break
                            
                    elif fvg['direction'] == 'Bearish':
                        # Check if price came back up to fill the gap
                        if row['High'] >= gap_start:
                            # Look for reversal after fill
                            remaining_data = subsequent_data.iloc[i+1:]
                            if len(remaining_data) > 0:
                                # Check for bearish reversal after fill
                                reversal_found = False
                                for j, (rev_timestamp, rev_row) in enumerate(remaining_data.iterrows()):
                                    if rev_row['Low'] < gap_end:  # Price moved back below gap
                                        reversal_found = True
                                        break
                                    if j >= 5:  # Limit search to next 5 candles
                                        break
                                
                                if reversal_found:
                                    ifvg = {
                                        'type': 'iFVG',
                                        'direction': 'Bearish',
                                        'timestamp': timestamp,
                                        'original_fvg': fvg,
                                        'fill_price': row['High'],
                                        'fill_percentage': ((row['High'] - gap_start) / gap_start) * 100,
                                        'reversal_confirmed': True,
                                        'volume': row['Volume']
                                    }
                                    ifvgs.append(ifvg)
                                    self.logger.debug(f"Bearish iFVG detected at {timestamp}")
                            break
                            
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error processing iFVG for timestamp {fvg_timestamp}: {str(e)}")
                continue
                
        return ifvgs
    
    def get_active_fvgs(self, data: pd.DataFrame, fvgs: List[Dict]) -> List[Dict]:
        """Get FVGs that haven't been filled yet"""
        active_fvgs = []
        
        if not fvgs:
            return active_fvgs
            
        current_price = data.iloc[-1]['Close']
        
        for fvg in fvgs:
            gap_start = fvg['gap_start']
            gap_end = fvg['gap_end']
            
            # Check if FVG is still active (not filled)
            if fvg['direction'] == 'Bullish':
                # Bullish FVG is active if current price is above gap_start
                if current_price > gap_start:
                    active_fvgs.append(fvg)
            elif fvg['direction'] == 'Bearish':
                # Bearish FVG is active if current price is below gap_start
                if current_price < gap_start:
                    active_fvgs.append(fvg)
                    
        return active_fvgs
    
    def analyze_symbol(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Analyze a single symbol for FVGs and iFVGs"""
        if data is None or data.empty:
            return {
                'symbol': symbol,
                'fvgs': [],
                'ifvgs': [],
                'active_fvgs': [],
                'recent_fvg': None,
                'recent_ifvg': None,
                'fvg_count': 0,
                'ifvg_count': 0,
                'analysis_timestamp': datetime.now()
            }
        
        # Detect FVGs and iFVGs
        fvgs = self.detect_fvg(data)
        ifvgs = self.detect_ifvg(data, fvgs)
        active_fvgs = self.get_active_fvgs(data, fvgs)
        
        # Get the most recent signals (within last 10 periods)
        recent_fvg = None
        recent_ifvg = None
        
        if fvgs:
            # Get FVGs from the last 10 periods
            recent_threshold = data.index[-10] if len(data) >= 10 else data.index[0]
            recent_fvgs = [fvg for fvg in fvgs if fvg['timestamp'] >= recent_threshold]
            if recent_fvgs:
                recent_fvg = recent_fvgs[-1]
        
        if ifvgs:
            # Get iFVGs from the last 10 periods
            recent_threshold = data.index[-10] if len(data) >= 10 else data.index[0]
            recent_ifvgs = [ifvg for ifvg in ifvgs if ifvg['timestamp'] >= recent_threshold]
            if recent_ifvgs:
                recent_ifvg = recent_ifvgs[-1]
        
        return {
            'symbol': symbol,
            'fvgs': fvgs,
            'ifvgs': ifvgs,
            'active_fvgs': active_fvgs,
            'recent_fvg': recent_fvg,
            'recent_ifvg': recent_ifvg,
            'fvg_count': len(fvgs),
            'ifvg_count': len(ifvgs),
            'active_fvg_count': len(active_fvgs),
            'analysis_timestamp': datetime.now(),
            'current_price': data.iloc[-1]['Close'] if not data.empty else None
        }
