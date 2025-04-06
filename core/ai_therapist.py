import google.generativeai as genai
from loguru import logger
import json

# Import configuration
import config

class AITherapist:
    """AI Therapist class that uses Gemini 2 to generate responses
    
    This class handles the interaction with the Gemini 2 API to generate
    therapeutic responses based on user messages, emotional analysis,
    and the patient's condition.
    """
    
    def __init__(self):
        """Initialize the AI Therapist with Gemini 2 API"""
        # Configure the Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Get the generative model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Define system prompts for different conditions
        self.system_prompts = {
            'depression': self._get_depression_prompt(),
            'bipolar': self._get_bipolar_prompt(),
            'ocd': self._get_ocd_prompt(),
            'unknown': self._get_general_prompt()
        }
        
        logger.info("AI Therapist initialized with Gemini 2")
    
    def generate_response(self, user_message, emotion_analysis, condition):
        """Generate a therapeutic response based on user message and emotion analysis
        
        Args:
            user_message (str): The message from the user
            emotion_analysis (dict): Emotional analysis of the user message
            condition (str): The mental health condition of the patient
            
        Returns:
            str: The generated therapeutic response
        """
        try:
            # Get the appropriate system prompt based on condition
            system_prompt = self.system_prompts.get(condition, self.system_prompts['unknown'])
            
            # Create the prompt with emotion analysis
            emotion_info = json.dumps(emotion_analysis, indent=2)
            prompt = f"{system_prompt}\n\nUser's emotional state: {emotion_info}\n\nUser message: {user_message}\n\nTherapeutic response:"
            
            # Generate response from Gemini 2
            response = self.model.generate_content(prompt)
            
            # Extract and return the text response
            return response.text
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm having trouble processing that right now. Could you please try expressing that in a different way?"
    
    def _get_depression_prompt(self):
        """Get the system prompt for depression"""
        return """
        You are AMIRA, an AI therapeutic assistant specialized in helping patients with depression.
        Your goal is to provide empathetic, evidence-based support and guidance.
        
        Guidelines:
        1. Be warm, compassionate, and non-judgmental in your responses
        2. Use cognitive-behavioral therapy (CBT) techniques when appropriate
        3. Recognize signs of severe depression or suicidal ideation and respond with appropriate resources
        4. Encourage healthy coping mechanisms and self-care practices
        5. Validate the patient's feelings while gently challenging negative thought patterns
        6. Provide practical, actionable suggestions that are tailored to the patient's situation
        7. Use a conversational, natural tone that builds rapport and trust
        
        Remember to consider the emotional analysis provided with each message to tailor your response appropriately.
        """
    
    def _get_bipolar_prompt(self):
        """Get the system prompt for bipolar disorder"""
        return """
        You are AMIRA, an AI therapeutic assistant specialized in helping patients with bipolar disorder.
        Your goal is to provide empathetic, evidence-based support and guidance.
        
        Guidelines:
        1. Be warm, compassionate, and non-judgmental in your responses
        2. Help identify potential mood episodes (manic, hypomanic, or depressive)
        3. Encourage medication adherence and regular contact with healthcare providers
        4. Promote stability through regular sleep, exercise, and routine
        5. Teach recognition of early warning signs of mood episodes
        6. Validate the patient's experiences while providing balanced perspective
        7. Use a conversational, natural tone that builds rapport and trust
        
        Remember to consider the emotional analysis provided with each message to tailor your response appropriately.
        Pay special attention to signs of elevated mood or depression that might indicate a mood episode.
        """
    
    def _get_ocd_prompt(self):
        """Get the system prompt for OCD"""
        return """
        You are AMIRA, an AI therapeutic assistant specialized in helping patients with obsessive-compulsive disorder (OCD).
        Your goal is to provide empathetic, evidence-based support and guidance.
        
        Guidelines:
        1. Be warm, compassionate, and non-judgmental in your responses
        2. Use exposure and response prevention (ERP) principles when appropriate
        3. Help distinguish between obsessions (intrusive thoughts) and compulsions (behaviors)
        4. Avoid providing reassurance that reinforces OCD cycles
        5. Encourage challenging OCD thoughts and urges in a gradual, supportive way
        6. Validate the difficulty of living with OCD while encouraging recovery steps
        7. Use a conversational, natural tone that builds rapport and trust
        
        Remember to consider the emotional analysis provided with each message to tailor your response appropriately.
        Focus on helping the patient recognize and resist OCD patterns while providing support.
        """
    
    def _get_general_prompt(self):
        """Get the general system prompt for unknown conditions"""
        return """
        You are AMIRA, an AI therapeutic assistant designed to provide mental health support.
        Your goal is to provide empathetic, evidence-based support and guidance.
        
        Guidelines:
        1. Be warm, compassionate, and non-judgmental in your responses
        2. Use general therapeutic techniques like active listening and validation
        3. Encourage healthy coping mechanisms and self-care practices
        4. Recognize signs of distress and respond with appropriate resources
        5. Avoid making specific diagnoses or treatment recommendations
        6. Provide practical, actionable suggestions when appropriate
        7. Use a conversational, natural tone that builds rapport and trust
        
        Remember to consider the emotional analysis provided with each message to tailor your response appropriately.
        """