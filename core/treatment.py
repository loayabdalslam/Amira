from loguru import logger
import google.generativeai as genai
import json

# Import configuration
import config

class TreatmentRecommender:
    """Treatment Recommender class that generates personalized therapeutic interventions
    
    This class provides evidence-based treatment recommendations and interventions
    tailored to the patient's specific condition, emotional state, and progress.
    """
    
    def __init__(self):
        """Initialize the Treatment Recommender with Gemini 2 API"""
        # Configure the Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Get the generative model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Define treatment approaches for different conditions
        self.treatment_approaches = {
            'depression': self._get_depression_approaches(),
            'bipolar': self._get_bipolar_approaches(),
            'ocd': self._get_ocd_approaches(),
            'unknown': self._get_general_approaches()
        }
        
        logger.info("Treatment Recommender initialized")
    
    def generate_recommendations(self, patient_data, session_history, emotion_analysis):
        """Generate personalized treatment recommendations
        
        Args:
            patient_data (dict): Patient information including condition
            session_history (list): History of previous therapy sessions
            emotion_analysis (dict): Current emotional state analysis
            
        Returns:
            dict: Treatment recommendations and interventions
        """
        try:
            # Get condition-specific approaches
            condition = patient_data.get('condition', 'unknown')
            approaches = self.treatment_approaches.get(condition, self.treatment_approaches['unknown'])
            
            # Create the prompt for treatment recommendations
            prompt = f"""
            Generate personalized therapeutic recommendations for a patient with the following profile:
            
            Patient Condition: {condition}
            Current Emotional State: {json.dumps(emotion_analysis)}
            
            Based on evidence-based approaches for this condition, including:
            {approaches}
            
            Generate 3-5 specific, actionable recommendations that address the patient's current emotional state
            and align with best practices for treating their condition. Include both immediate coping strategies
            and longer-term therapeutic interventions.
            
            Format the response as a JSON object with the following structure:
            {{"immediate_strategies": ["string"],
              "therapeutic_interventions": ["string"],
              "self_care_recommendations": ["string"],
              "resources": ["string"],
              "progress_indicators": ["string"]
            }}
            
            JSON response:
            """
            
            # Generate recommendations from Gemini 2
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
                recommendations = json.loads(json_str)
                return recommendations
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing recommendations JSON: {e}")
                # Fallback to basic recommendations
                return {
                    "immediate_strategies": ["Practice deep breathing for 5 minutes"],
                    "therapeutic_interventions": ["Consider keeping a mood journal"],
                    "self_care_recommendations": ["Ensure you're getting adequate sleep"],
                    "resources": ["Speak with a mental health professional"],
                    "progress_indicators": ["Notice improvements in daily functioning"]
                }
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # Return default recommendations in case of error
            return {
                "immediate_strategies": ["Practice deep breathing for 5 minutes"],
                "therapeutic_interventions": ["Consider keeping a mood journal"],
                "self_care_recommendations": ["Ensure you're getting adequate sleep"],
                "resources": ["Speak with a mental health professional"],
                "progress_indicators": ["Notice improvements in daily functioning"]
            }
    
    def _get_depression_approaches(self):
        """Get evidence-based approaches for depression"""
        return """
        1. Cognitive-Behavioral Therapy (CBT) techniques to identify and challenge negative thought patterns
        2. Behavioral activation to increase engagement in rewarding activities
        3. Mindfulness and acceptance-based approaches
        4. Interpersonal therapy strategies to address relationship issues
        5. Lifestyle modifications including exercise, sleep hygiene, and nutrition
        6. Social connection and support building
        7. Stress reduction and relaxation techniques
        """
    
    def _get_bipolar_approaches(self):
        """Get evidence-based approaches for bipolar disorder"""
        return """
        1. Mood monitoring and early warning sign identification
        2. Sleep regulation and routine maintenance
        3. Stress management and trigger avoidance
        4. Interpersonal and social rhythm therapy techniques
        5. Cognitive-behavioral strategies for managing mood episodes
        6. Medication adherence support
        7. Psychoeducation about bipolar disorder
        8. Family involvement and communication strategies
        """
    
    def _get_ocd_approaches(self):
        """Get evidence-based approaches for OCD"""
        return """
        1. Exposure and Response Prevention (ERP) techniques
        2. Cognitive strategies to address obsessional thoughts
        3. Mindfulness-based approaches for OCD
        4. Acceptance and Commitment Therapy principles
        5. Habit reversal training
        6. Stress management and anxiety reduction
        7. Family accommodation reduction strategies
        8. Relapse prevention planning
        """
    
    def _get_general_approaches(self):
        """Get general therapeutic approaches"""
        return """
        1. Supportive listening and validation
        2. Basic cognitive-behavioral techniques
        3. Mindfulness and stress reduction
        4. Emotion regulation skills
        5. Problem-solving strategies
        6. Self-care and lifestyle improvements
        7. Social support enhancement
        8. Goal-setting and motivation building
        """