import unittest
import pandas as pd
import numpy as np
import os
import tempfile

from hives_calculations import (
    calculate_statistics, 
    apply_score_bell,
    calculate_percentage_score_matrix,
    calculate_criteria_weights,
    calculate_final_scores
)
from hives import hives_algorithm

class TestHivesCalculations(unittest.TestCase):
    """Test cases for HIVES calculation functions."""
    
    def setUp(self):
        """Set up test data."""
        # Sample weights data
        self.weights_data = pd.DataFrame({
            'C1': [80, 70, 90, 85],
            'C2': [60, 65, 70, 75]
        })
        
        # Sample agents data
        self.agents_data = pd.DataFrame({
            'C1': [85, 70, 90],
            'C2': [75, 80, 65]
        }, index=['A1', 'A2', 'A3'])
        
        # Statistical values for testing
        self.min_val, self.q1_val = 60, 70
        self.sicp_val, self.q3_val = 80, 90
        self.max_val = 100
        
    def test_calculate_statistics(self):
        """Test the calculate_statistics function."""
        stats = calculate_statistics(self.weights_data)
        
        # Check that the result has the expected shape and values
        self.assertIsInstance(stats, pd.DataFrame)
        self.assertEqual(stats.shape, (5, 2))
        self.assertTrue(all(col in stats.columns for col in ['C1', 'C2']))
        self.assertTrue(all(idx in stats.index for idx in ['Min', 'Q1', 'SICP', 'Q3', 'Max']))
        
        # Check that Min is less than or equal to Q1, etc.
        for col in stats.columns:
            self.assertLessEqual(stats.loc['Min', col], stats.loc['Q1', col])
            self.assertLessEqual(stats.loc['Q1', col], stats.loc['SICP', col])
            self.assertLessEqual(stats.loc['SICP', col], stats.loc['Q3', col])
            self.assertLessEqual(stats.loc['Q3', col], stats.loc['Max', col])
    
    def test_apply_score_bell(self):
        """Test the apply_score_bell function."""
        # Test various zones
        # Zone 1 (below Q1)
        score_zone1 = apply_score_bell(65, self.min_val, self.q1_val, 
                                      self.sicp_val, self.q3_val, self.max_val)
        self.assertGreaterEqual(score_zone1, 0)
        self.assertLessEqual(score_zone1, 50)
        
        # Zone 2 (between Q1 and SICP)
        score_zone2 = apply_score_bell(75, self.min_val, self.q1_val, 
                                      self.sicp_val, self.q3_val, self.max_val)
        self.assertGreaterEqual(score_zone2, 50)
        self.assertLessEqual(score_zone2, 100)
        
        # Zone 3 (between SICP and Q3)
        score_zone3 = apply_score_bell(85, self.min_val, self.q1_val, 
                                      self.sicp_val, self.q3_val, self.max_val)
        self.assertGreaterEqual(score_zone3, 50)
        self.assertLessEqual(score_zone3, 100)
        
        # Zone 4 (above Q3)
        score_zone4 = apply_score_bell(95, self.min_val, self.q1_val, 
                                      self.sicp_val, self.q3_val, self.max_val)
        self.assertGreaterEqual(score_zone4, 0)
        self.assertLessEqual(score_zone4, 50)
        
        # Test boundary values
        self.assertEqual(apply_score_bell(self.min_val, self.min_val, self.q1_val, 
                                         self.sicp_val, self.q3_val, self.max_val), 1.0)
        
    def test_percentage_score_matrix(self):
        """Test the calculate_percentage_score_matrix function."""
        hsm = np.array([[80, 70], [90, 85], [75, 65]])
        result = calculate_percentage_score_matrix(hsm)
        
        # Check that the result has the expected shape
        self.assertEqual(result.shape, hsm.shape)
        
        # Check that each column sums to approximately 100%
        for col in range(result.shape[1]):
            self.assertAlmostEqual(np.sum(result[:, col]), 100, places=5)
    
    def test_criteria_weights(self):
        """Test the calculate_criteria_weights function."""
        final_weights = pd.DataFrame({
            'C1': [0.3, 0.4, 0.3],
            'C2': [0.25, 0.5, 0.25]
        })
        orig_weights = pd.DataFrame({
            'C1': [80, 75, 85],
            'C2': [70, 65, 60]
        })
        
        result = calculate_criteria_weights(final_weights, orig_weights)
        
        # Check that the result is a list of the expected length
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        # Check that weights sum to approximately 100
        self.assertAlmostEqual(sum(result), 100, places=5)
    
    def test_final_scores(self):
        """Test the calculate_final_scores function."""
        weights = [60, 40]
        result = calculate_final_scores(weights, self.agents_data)
        
        # Check that the result has the expected shape and columns
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape[0], len(self.agents_data))
        self.assertTrue('Total Score' in result.columns)
        self.assertTrue('Ranking' in result.columns)
        
        # Check that rankings are integers starting from 1
        rankings = result['Ranking'].values
        self.assertTrue(all(isinstance(r, (int, np.integer)) for r in rankings))
        self.assertTrue(all(r >= 1 for r in rankings))

class TestHivesAlgorithm(unittest.TestCase):
    """Test cases for the main HIVES algorithm."""
    
    def setUp(self):
        """Create temporary CSV files for testing."""
        # Create temp directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Sample agents data
        self.agents_data = pd.DataFrame({
            'C1': [85, 70, 90],
            'C2': [75, 80, 65]
        }, index=['A1', 'A2', 'A3'])
        
        # Sample weights data
        self.weights_data = pd.DataFrame({
            'C1': [80, 70, 90, 85],
            'C2': [60, 65, 70, 75]
        })
        
        # Write to temporary CSV files
        self.agents_file = os.path.join(self.temp_dir.name, 'agents.csv')
        self.weights_file = os.path.join(self.temp_dir.name, 'weights.csv')
        
        self.agents_data.to_csv(self.agents_file)
        self.weights_data.to_csv(self.weights_file)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_hives_algorithm(self):
        """Test the main HIVES algorithm."""
        result = hives_algorithm(self.agents_file, self.weights_file)
        
        # Check that the result has the expected shape and columns
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape[0], len(self.agents_data))
        self.assertTrue('Candidates' in result.columns)
        self.assertTrue('Total Score' in result.columns)
        self.assertTrue('Ranking' in result.columns)
        
        # Check that rankings are valid
        rankings = result['Ranking'].values
        self.assertEqual(len(rankings), len(self.agents_data))
        self.assertTrue(all(r >= 1 for r in rankings))
        self.assertTrue(all(r <= len(self.agents_data) for r in rankings))

if __name__ == '__main__':
    unittest.main()
