import google.generativeai as genai
from loguru import logger
import json

# Import configuration
import config
from core.localization import Localization

class EmotionAnalyzer:
    """Emotion Analyzer class that uses Gemini 2 to analyze emotions in text
    
    This class handles the analysis of emotional content in user messages,
    providing insights into the patient's emotional state to guide the
    therapeutic response.
    """
    
    def __init__(self, language='en'):
        """Initialize the Emotion Analyzer with Gemini 2 API
        
        Args:
            language (str, optional): Language code ('en' or 'ar')
        """
        # Configure the Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Get the generative model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize localization
        self.localization = Localization(language)
        
        logger.info(f"Emotion Analyzer initialized with Gemini 2 in language: {language}")
    
    def analyze(self, text, language=None):
        """Analyze the emotional content of a text message
        
        Args:
            text (str): The text message to analyze
            language (str, optional): Language code ('en' or 'ar'). If None, will attempt to detect language.
            
        Returns:
            dict: A dictionary containing emotional analysis results
        """
        try:
            # Detect language if not provided
            detected_language = language
            if not detected_language:
                # Create prompt for language detection
                lang_detect_prompt = f"""
                Identify the language of the following text. Return only the language code:
                'en' for English or 'ar' for Arabic.
                
                Text: {text}
                
                Language code (en/ar):
                """
                
                lang_response = self.model.generate_content(lang_detect_prompt)
                detected_language = lang_response.text.strip().lower()
                
                # Validate language code
                if detected_language not in ['en', 'ar']:
                    detected_language = 'en'  # Default to English if detection fails
                
                logger.info(f"Detected language: {detected_language}")
            
            # Update localization if needed
            if self.localization.language != detected_language:
                self.localization.switch_language(detected_language)
            
            # Create the prompt for emotion analysis
            prompt = f"""
            Analyze the emotional content of the following text in {detected_language} language and provide a detailed assessment.
            Focus on identifying the primary emotions, their intensity, and any patterns or concerns.
            
            For mental health monitoring, also assess:
            1. Overall mood state (e.g., depressed, anxious, stable, elevated)
            2. Any signs of cognitive distortions or unhealthy thought patterns
            3. Potential risk factors or warning signs that might require attention
            4. Changes in emotional state compared to a neutral baseline
            
            Format the response as a JSON object with the following structure:
            {{"primary_emotion": "string",
              "emotion_intensity": "low|medium|high",
              "mood_state": "string",
              "cognitive_patterns": ["string"],
              "risk_factors": ["string"],
              "additional_observations": "string",
              "detected_language": "{detected_language}"
            }}
            
            Text to analyze: {text}
            
            JSON response:
            """
            
            # Generate analysis from Gemini 2
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                # Extract JSON from the response text
                json_str = response.text.strip()
                # Handle potential markdown code block formatting
                if json_str.startswith('```json'):
                    json_str = json_str.replace('```json', '').replace('```', '').strip()
                elif json_str.startswith('```'):
                    json_str = json_str.replace('```', '').strip()
                
                # Parse the JSON
                analysis = json.loads(json_str)
                return analysis
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing emotion analysis JSON: {e}")
                # Fallback to a basic analysis
                return {
                    "primary_emotion": "unknown",
                    "emotion_intensity": "medium",
                    "mood_state": "unclear",
                    "cognitive_patterns": [],
                    "risk_factors": [],
                    "additional_observations": "Unable to analyze emotional content accurately."
                }
        
        except Exception as e:
            logger.error(f"Error analyzing emotions: {e}")
            # Return a default analysis in case of error
            return {
                "primary_emotion": "unknown",
                "emotion_intensity": "medium",
                "mood_state": "unclear",
                "cognitive_patterns": [],
                "risk_factors": [],
                "additional_observations": "Error occurred during emotional analysis."
            }