import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fvg_detector import FVGDetector

class TestFVGDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = FVGDetector(threshold=0.001)
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01 09:30:00', periods=20, freq='5T')
        self.sample_data = pd.DataFrame({
            'Open': [100 + i for i in range(20)],
            'High': [100.5 + i for i in range(20)],
            'Low': [99.5 + i for i in range(20)],
            'Close': [100.2 + i for i in range(20)],
            'Volume': [1000 + i*100 for i in range(20)]
        }, index=dates)
        
        # Create data with a clear bullish FVG
        self.bullish_fvg_data = self.sample_data.copy()
        # Create a gap: previous high = 102.5, current low = 105.0
        self.bullish_fvg_data.loc[self.bullish_fvg_data.index[5], 'Low'] = 105.0
        self.bullish_fvg_data.loc[self.bullish_fvg_data.index[5], 'High'] = 105.5
        self.bullish_fvg_data.loc[self.bullish_fvg_data.index[5], 'Close'] = 105.2
        
        # Create data with a clear bearish FVG
        self.bearish_fvg_data = self.sample_data.copy()
        # Create a gap: previous low = 102.5, current high = 100.0
        self.bearish_fvg_data.loc[self.bearish_fvg_data.index[5], 'High'] = 100.0
        self.bearish_fvg_data.loc[self.bearish_fvg_data.index[5], 'Low'] = 99.5
        self.bearish_fvg_data.loc[self.bearish_fvg_data.index[5], 'Close'] = 99.8
    
    def test_detect_bullish_fvg(self):
        """Test detection of bullish FVG"""
        fvgs = self.detector.detect_fvg(self.bullish_fvg_data)
        
        # Should detect at least one FVG
        self.assertGreater(len(fvgs), 0)
        
        # Check if bullish FVG is detected
        bullish_fvgs = [fvg for fvg in fvgs if fvg['direction'] == 'Bullish']
        self.assertGreater(len(bullish_fvgs), 0)
        
        # Check FVG properties
        fvg = bullish_fvgs[0]
        self.assertEqual(fvg['type'], 'FVG')
        self.assertEqual(fvg['direction'], 'Bullish')
        self.assertGreater(fvg['gap_size'], 0)
        self.assertIn('timestamp', fvg)
        self.assertIn('gap_start', fvg)
        self.assertIn('gap_end', fvg)
        self.assertIn('gap_percentage', fvg)
    
    def test_detect_bearish_fvg(self):
        """Test detection of bearish FVG"""
        fvgs = self.detector.detect_fvg(self.bearish_fvg_data)
        
        # Should detect at least one FVG
        self.assertGreater(len(fvgs), 0)
        
        # Check if bearish FVG is detected
        bearish_fvgs = [fvg for fvg in fvgs if fvg['direction'] == 'Bearish']
        self.assertGreater(len(bearish_fvgs), 0)
        
        # Check FVG properties
        fvg = bearish_fvgs[0]
        self.assertEqual(fvg['type'], 'FVG')
        self.assertEqual(fvg['direction'], 'Bearish')
        self.assertGreater(fvg['gap_size'], 0)
        self.assertIn('timestamp', fvg)
        self.assertIn('gap_start', fvg)
        self.assertIn('gap_end', fvg)
        self.assertIn('gap_percentage', fvg)
    
    def test_no_fvg_detection(self):
        """Test that no FVG is detected in regular data"""
        fvgs = self.detector.detect_fvg(self.sample_data)
        
        # Should not detect any significant FVGs in regular trending data
        self.assertEqual(len(fvgs), 0)
    
    def test_detect_ifvg(self):
        """Test detection of iFVG"""
        # First detect FVGs
        fvgs = self.detector.detect_fvg(self.bullish_fvg_data)
        
        # Create data where price comes back to fill the gap
        ifvg_data = self.bullish_fvg_data.copy()
        if fvgs:
            fvg = fvgs[0]
            gap_start = fvg['gap_start']
            
            # Add candles where price comes back down to fill the gap
            for i in range(10, 15):
                if i < len(ifvg_data):
                    ifvg_data.loc[ifvg_data.index[i], 'Low'] = gap_start - 0.5
                    ifvg_data.loc[ifvg_data.index[i], 'Close'] = gap_start - 0.2
        
        ifvgs = self.detector.detect_ifvg(ifvg_data, fvgs)
        
        # Should detect iFVG if conditions are met
        if ifvgs:
            ifvg = ifvgs[0]
            self.assertEqual(ifvg['type'], 'iFVG')
            self.assertIn('direction', ifvg)
            self.assertIn('fill_price', ifvg)
            self.assertIn('original_fvg', ifvg)
    
    def test_analyze_symbol(self):
        """Test complete symbol analysis"""
        analysis = self.detector.analyze_symbol('TEST', self.sample_data)
        
        # Check analysis structure
        expected_keys = [
            'symbol', 'fvgs', 'ifvgs', 'active_fvgs', 'recent_fvg', 
            'recent_ifvg', 'fvg_count', 'ifvg_count', 'active_fvg_count',
            'analysis_timestamp', 'current_price'
        ]
        
        for key in expected_keys:
            self.assertIn(key, analysis)
        
        self.assertEqual(analysis['symbol'], 'TEST')
        self.assertIsInstance(analysis['fvgs'], list)
        self.assertIsInstance(analysis['ifvgs'], list)
        self.assertIsInstance(analysis['active_fvgs'], list)
        self.assertIsInstance(analysis['fvg_count'], int)
        self.assertIsInstance(analysis['ifvg_count'], int)
        self.assertIsInstance(analysis['active_fvg_count'], int)
    
    def test_analyze_symbol_with_empty_data(self):
        """Test symbol analysis with empty data"""
        empty_data = pd.DataFrame()
        analysis = self.detector.analyze_symbol('TEST', empty_data)
        
        # Should return default values
        self.assertEqual(analysis['symbol'], 'TEST')
        self.assertEqual(analysis['fvgs'], [])
        self.assertEqual(analysis['ifvgs'], [])
        self.assertEqual(analysis['active_fvgs'], [])
        self.assertIsNone(analysis['recent_fvg'])
        self.assertIsNone(analysis['recent_ifvg'])
        self.assertEqual(analysis['fvg_count'], 0)
        self.assertEqual(analysis['ifvg_count'], 0)
        self.assertEqual(analysis['active_fvg_count'], 0)
        self.assertIsNone(analysis['current_price'])
    
    def test_get_active_fvgs(self):
        """Test getting active FVGs"""
        fvgs = self.detector.detect_fvg(self.bullish_fvg_data)
        active_fvgs = self.detector.get_active_fvgs(self.bullish_fvg_data, fvgs)
        
        # Active FVGs should be a subset of all FVGs
        self.assertLessEqual(len(active_fvgs), len(fvgs))
        
        # All active FVGs should be in the original FVG list
        for active_fvg in active_fvgs:
            self.assertIn(active_fvg, fvgs)
    
    def test_threshold_filtering(self):
        """Test that threshold filtering works correctly"""
        # Create detector with high threshold
        high_threshold_detector = FVGDetector(threshold=0.1)  # 10% threshold
        
        # Should detect fewer FVGs with high threshold
        fvgs_low_threshold = self.detector.detect_fvg(self.bullish_fvg_data)
        fvgs_high_threshold = high_threshold_detector.detect_fvg(self.bullish_fvg_data)
        
        self.assertLessEqual(len(fvgs_high_threshold), len(fvgs_low_threshold))
    
    def test_minimum_data_requirement(self):
        """Test that minimum data requirements are enforced"""
        # Create data with less than 3 candles
        minimal_data = self.sample_data.iloc[:2]
        
        fvgs = self.detector.detect_fvg(minimal_data)
        
        # Should return empty list for insufficient data
        self.assertEqual(len(fvgs), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
