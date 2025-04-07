import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.emotion_analyzer import EmotionAnalyzer

class TestEmotionAnalyzer(unittest.TestCase):
    """Test cases for the EmotionAnalyzer class"""
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def setUp(self, mock_configure, mock_model_class):
        """Set up the test environment"""
        # Create a mock model instance
        self.mock_model = MagicMock()
        mock_model_class.return_value = self.mock_model
        
        # Initialize the EmotionAnalyzer
        self.analyzer = EmotionAnalyzer()
    
    def test_analyze_success(self):
        """Test successful emotion analysis"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "primary_emotion": "sadness",
            "emotion_intensity": "high",
            "mood_state": "depressed",
            "cognitive_patterns": ["catastrophizing", "black-and-white thinking"],
            "risk_factors": ["social isolation"],
            "additional_observations": "Shows signs of hopelessness"
        })
        
        # Configure the mock model to return the mock response
        self.mock_model.generate_content.return_value = mock_response
        
        # Call the analyze method
        result = self.analyzer.analyze("I feel so sad and alone today.")
        
        # Verify the result
        self.assertEqual(result["primary_emotion"], "sadness")
        self.assertEqual(result["emotion_intensity"], "high")
        self.assertEqual(result["mood_state"], "depressed")
        self.assertIn("catastrophizing", result["cognitive_patterns"])
        self.assertIn("social isolation", result["risk_factors"])
    
    def test_analyze_json_error(self):
        """Test handling of JSON parsing errors"""
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        
        # Configure the mock model to return the mock response
        self.mock_model.generate_content.return_value = mock_response
        
        # Call the analyze method
        result = self.analyzer.analyze("Test message")
        
        # Verify fallback behavior
        self.assertEqual(result["primary_emotion"], "unknown")
        self.assertEqual(result["emotion_intensity"], "medium")
        self.assertEqual(result["mood_state"], "unclear")
        self.assertEqual(result["cognitive_patterns"], [])
        self.assertEqual(result["risk_factors"], [])
    
    def test_analyze_api_error(self):
        """Test handling of API errors"""
        # Configure the mock model to raise an exception
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        # Call the analyze method
        result = self.analyzer.analyze("Test message")
        
        # Verify fallback behavior
        self.assertEqual(result["primary_emotion"], "unknown")
        self.assertEqual(result["emotion_intensity"], "medium")
        self.assertEqual(result["mood_state"], "unclear")
        self.assertEqual(result["cognitive_patterns"], [])
        self.assertEqual(result["risk_factors"], [])
        self.assertIn("Error occurred", result["additional_observations"])

if __name__ == '__main__':
    unittest.main()