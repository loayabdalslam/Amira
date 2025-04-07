import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_therapist import AITherapist

class TestAITherapist(unittest.TestCase):
    """Test cases for the AITherapist class"""
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def setUp(self, mock_configure, mock_model_class):
        """Set up the test environment"""
        # Create a mock model instance
        self.mock_model = MagicMock()
        mock_model_class.return_value = self.mock_model
        
        # Initialize the AITherapist
        self.therapist = AITherapist()
    
    def test_generate_response_depression(self):
        """Test response generation for depression condition"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.text = "I understand you're feeling down today. Let's talk about some strategies that might help."
        
        # Configure the mock model to return the mock response
        self.mock_model.generate_content.return_value = mock_response
        
        # Sample emotion analysis
        emotion_analysis = {
            "primary_emotion": "sadness",
            "emotion_intensity": "high",
            "mood_state": "depressed",
            "cognitive_patterns": ["negative self-talk"],
            "risk_factors": [],
            "additional_observations": "Shows signs of low mood"
        }
        
        # Call the generate_response method
        result = self.therapist.generate_response(
            "I've been feeling really sad lately", 
            emotion_analysis, 
            "depression"
        )
        
        # Verify the result
        self.assertEqual(result, mock_response.text)
        
        # Verify that the correct prompt was used
        call_args = self.mock_model.generate_content.call_args[0][0]
        self.assertIn("depression", self.therapist.system_prompts)
        self.assertIn("sadness", call_args)
        self.assertIn("depressed", call_args)
    
    def test_generate_response_bipolar(self):
        """Test response generation for bipolar condition"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.text = "I notice you're feeling quite energetic. Let's talk about maintaining balance."
        
        # Configure the mock model to return the mock response
        self.mock_model.generate_content.return_value = mock_response
        
        # Sample emotion analysis
        emotion_analysis = {
            "primary_emotion": "excitement",
            "emotion_intensity": "high",
            "mood_state": "elevated",
            "cognitive_patterns": ["racing thoughts"],
            "risk_factors": ["reduced sleep"],
            "additional_observations": "Shows signs of elevated mood"
        }
        
        # Call the generate_response method
        result = self.therapist.generate_response(
            "I have so many ideas and I feel amazing!", 
            emotion_analysis, 
            "bipolar"
        )
        
        # Verify the result
        self.assertEqual(result, mock_response.text)
        
        # Verify that the correct prompt was used
        call_args = self.mock_model.generate_content.call_args[0][0]
        self.assertIn("bipolar", self.therapist.system_prompts)
        self.assertIn("excitement", call_args)
        self.assertIn("elevated", call_args)
    
    def test_generate_response_ocd(self):
        """Test response generation for OCD condition"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.text = "I understand these thoughts are causing you distress. Let's work on some exposure techniques."
        
        # Configure the mock model to return the mock response
        self.mock_model.generate_content.return_value = mock_response
        
        # Sample emotion analysis
        emotion_analysis = {
            "primary_emotion": "anxiety",
            "emotion_intensity": "high",
            "mood_state": "anxious",
            "cognitive_patterns": ["intrusive thoughts", "perfectionism"],
            "risk_factors": [],
            "additional_observations": "Shows signs of compulsive checking"
        }
        
        # Call the generate_response method
        result = self.therapist.generate_response(
            "I can't stop checking if I locked the door", 
            emotion_analysis, 
            "ocd"
        )
        
        # Verify the result
        self.assertEqual(result, mock_response.text)
        
        # Verify that the correct prompt was used
        call_args = self.mock_model.generate_content.call_args[0][0]
        self.assertIn("ocd", self.therapist.system_prompts)
        self.assertIn("anxiety", call_args)
        self.assertIn("intrusive thoughts", call_args)
    
    def test_generate_response_unknown_condition(self):
        """Test response generation for unknown condition"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.text = "I hear that you're feeling frustrated. Let's explore that together."
        
        # Configure the mock model to return the mock response
        self.mock_model.generate_content.return_value = mock_response
        
        # Sample emotion analysis
        emotion_analysis = {
            "primary_emotion": "frustration",
            "emotion_intensity": "medium",
            "mood_state": "irritable",
            "cognitive_patterns": [],
            "risk_factors": [],
            "additional_observations": ""
        }
        
        # Call the generate_response method with an unknown condition
        result = self.therapist.generate_response(
            "I'm so annoyed with everything", 
            emotion_analysis, 
            "unknown_condition"
        )
        
        # Verify the result
        self.assertEqual(result, mock_response.text)
        
        # Verify that the general prompt was used
        call_args = self.mock_model.generate_content.call_args[0][0]
        self.assertIn("unknown", self.therapist.system_prompts)
        self.assertIn("frustration", call_args)
    
    def test_generate_response_api_error(self):
        """Test handling of API errors"""
        # Configure the mock model to raise an exception
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        # Call the generate_response method
        result = self.therapist.generate_response(
            "Test message", 
            {"primary_emotion": "neutral"}, 
            "depression"
        )
        
        # Verify fallback behavior
        self.assertIn("I'm having trouble processing", result)

if __name__ == '__main__':
    unittest.main()