"""Letting Go Technique Module for AMIRA

This module implements the Letting Go technique by David R. Hawkins,
which helps patients release negative emotions by acknowledging and accepting them.
"""

from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class LettingGoTechnique:
    """Implementation of the Letting Go technique by David R. Hawkins
    
    This class provides methods for guiding patients through the Letting Go technique,
    which involves identifying emotions, feeling them fully, and then releasing them.
    """
    
    def __init__(self, localization):
        """Initialize the LettingGoTechnique object
        
        Args:
            localization: Localization object for multilingual support
        """
        self.localization = localization
        logger.info("Letting Go Technique module initialized")
    
    def get_introduction(self):
        """Get the introduction to the Letting Go technique
        
        Returns:
            str: Introduction text explaining the technique
        """
        return self.localization.get_text('letting_go_intro')
    
    def get_step_prompt(self, step):
        """Get the prompt for a specific step in the Letting Go technique
        
        Args:
            step (int): Step number (1-4)
            
        Returns:
            str: Prompt text for the specified step
        """
        key = f'letting_go_step{step}'
        return self.localization.get_text(key)
    
    def get_all_steps(self):
        """Get all steps of the Letting Go technique
        
        Returns:
            list: List of all step prompts
        """
        return [
            self.get_step_prompt(1),
            self.get_step_prompt(2),
            self.get_step_prompt(3),
            self.get_step_prompt(4)
        ]
    
    def get_prompt_keyboard(self):
        """Get the keyboard markup for asking if user wants to try the technique
        
        Returns:
            InlineKeyboardMarkup: Keyboard with yes/no options
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    self.localization.get_text('letting_go_yes'), 
                    callback_data="letting_go_yes"
                ),
                InlineKeyboardButton(
                    self.localization.get_text('letting_go_no'), 
                    callback_data="letting_go_no"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_progress_keyboard(self, session_id):
        """Get the keyboard markup for tracking progress after a message
        
        Args:
            session_id: The current session ID for tracking
            
        Returns:
            InlineKeyboardMarkup: Keyboard with progress tracking button
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    self.localization.get_text('calculate_progress'), 
                    callback_data=f"progress_{session_id}"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def process_emotion(self, emotion):
        """Process an identified emotion and provide guidance for letting it go
        
        Args:
            emotion (str): The identified emotion
            
        Returns:
            str: Guidance text for processing and releasing the emotion
        """
        # This would typically contain more sophisticated logic based on the emotion
        # For now, we'll return a generic response
        return (
            f"I understand you're feeling {emotion}. The Letting Go technique teaches us "
            f"that we can release this emotion by fully acknowledging it without judgment. "
            f"Take a moment to feel where this {emotion} is in your body. Then, ask yourself "
            f"if you're willing to let it go, even just a little bit. Remember, letting go "
            f"is a choice we can make at any moment."
        )
    
    def track_progress(self, patient_data, session_data):
        """Track the patient's progress with the Letting Go technique
        
        Args:
            patient_data: Patient data from the database
            session_data: Current session data
            
        Returns:
            dict: Progress metrics
        """
        # This would typically analyze session data to measure progress
        # For now, we'll return a simple metrics object
        
        # Count interactions where letting go was used
        letting_go_count = 0
        for interaction in session_data.get('interactions', []):
            metadata = interaction.get('metadata', {})
            if metadata.get('technique') == 'letting_go':
                letting_go_count += 1
        
        # Calculate simple metrics
        metrics = {
            'technique_used_count': letting_go_count,
            'progress_percentage': min(100, letting_go_count * 10),  # Simple calculation
            'technique': 'letting_go'
        }
        
        return metrics