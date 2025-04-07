"""Session Management module for AMIRA

This module provides functionality for tracking and managing therapy sessions,
storing conversation history, and generating reports between sessions.
"""

import datetime
from loguru import logger
import json

# Import core modules
from core.emotion_analyzer import EmotionAnalyzer
from core.localization import Localization
from data.models import Session, Interaction, Report

class SessionManager:
    """Session Manager class for handling therapy sessions
    
    This class manages the lifecycle of therapy sessions, including:
    - Starting and ending sessions
    - Tracking conversation history
    - Generating session summaries and reports
    - Analyzing psychological conditions based on conversation content
    """
    
    def __init__(self, db, language='en'):
        """Initialize the Session Manager
        
        Args:
            db: MongoDB database connection
            language (str, optional): Language code ('en' or 'ar')
        """
        self.db = db
        self.emotion_analyzer = EmotionAnalyzer()
        self.localization = Localization(language)
        logger.info(f"Session Manager initialized with language: {language}")
    
    def start_session(self, patient_id):
        """Start a new therapy session
        
        Args:
            patient_id: The ID of the patient
            
        Returns:
            dict: The session data
        """
        # Create a new session
        session = {
            "patient_id": patient_id,
            "start_time": datetime.datetime.now(),
            "interactions": [],
            "session_id": str(datetime.datetime.now().timestamp()),
            "metadata": {
                "condition_classifications": [],
                "emotional_states": [],
                "techniques_used": []
            }
        }
        
        logger.info(f"Started new session for patient {patient_id}")
        return session
    
    def end_session(self, session_data):
        """End a therapy session and save it to the database
        
        Args:
            session_data (dict): The session data
            
        Returns:
            str: The ID of the saved session
        """
        # Update end time
        session_data["end_time"] = datetime.datetime.now()
        
        # Generate session summary
        summary = self._generate_session_summary(session_data)
        session_data["summary"] = summary
        
        # Create Session object
        session = Session(
            patient_id=session_data["patient_id"],
            start_time=session_data["start_time"],
            end_time=session_data["end_time"],
            interactions=session_data["interactions"],
            summary=summary,
            metrics=self._calculate_session_metrics(session_data)
        )
        
        # Save to database
        session_id = self.db.sessions.insert_one(session.to_dict()).inserted_id
        
        logger.info(f"Ended session for patient {session_data['patient_id']}")
        return str(session_id)
    
    def add_interaction(self, session_data, user_message, bot_response, emotion_analysis=None):
        """Add an interaction to the current session
        
        Args:
            session_data (dict): The session data
            user_message (str): Message from the user
            bot_response (str): Response from the bot
            emotion_analysis (dict, optional): Emotional analysis of the user message
            
        Returns:
            dict: Updated session data
        """
        # Analyze emotions if not provided
        if not emotion_analysis:
            emotion_analysis = self.emotion_analyzer.analyze(user_message)
        
        # Create interaction
        interaction = Interaction(
            timestamp=datetime.datetime.now(),
            user_message=user_message,
            bot_response=bot_response,
            emotion_analysis=emotion_analysis,
            metadata={
                "session_id": session_data.get("session_id"),
                "user_id": session_data.get("patient_id")
            }
        )
        
        # Add to session
        session_data["interactions"].append(interaction.to_dict())
        
        # Update emotional states in metadata
        if emotion_analysis and "primary_emotion" in emotion_analysis:
            session_data["metadata"]["emotional_states"].append(emotion_analysis["primary_emotion"])
        
        # Classify psychological condition based on conversation
        if len(session_data["interactions"]) % 5 == 0:  # Classify every 5 interactions
            condition_classification = self._classify_psychological_condition(session_data)
            if condition_classification:
                session_data["metadata"]["condition_classifications"].append(condition_classification)
        
        return session_data
    
    def get_previous_session_report(self, patient_id):
        """Get a report from the previous session
        
        Args:
            patient_id: The ID of the patient
            
        Returns:
            dict: The previous session report or None if no previous session
        """
        # Get the most recent completed session
        previous_session = self.db.sessions.find_one(
            {"patient_id": patient_id, "end_time": {"$exists": True}},
            sort=[("end_time", -1)]
        )
        
        if not previous_session:
            return None
        
        # Get patient data
        patient = self.db.patients.find_one({"_id": patient_id})
        language = patient.get("language", "en") if patient else "en"
        
        # Update localization
        self.localization.switch_language(language)
        
        # Generate a brief report
        report = {
            "session_date": previous_session["end_time"].strftime("%Y-%m-%d"),
            "session_duration": str(previous_session["end_time"] - previous_session["start_time"]),
            "interaction_count": len(previous_session.get("interactions", [])),
            "summary": previous_session.get("summary", self.localization.get_text("no_summary_available")),
            "emotional_trends": self._extract_emotional_trends(previous_session),
            "progress_indicators": self._extract_progress_indicators(previous_session),
            "recommendations": previous_session.get("metrics", {}).get("recommendations", [])
        }
        
        return report
    
    def _generate_session_summary(self, session_data):
        """Generate a summary of the session
        
        Args:
            session_data (dict): The session data
            
        Returns:
            str: The session summary
        """
        # Extract key information
        interaction_count = len(session_data.get("interactions", []))
        duration = datetime.datetime.now() - session_data.get("start_time", datetime.datetime.now())
        
        # Extract emotional states
        emotional_states = session_data.get("metadata", {}).get("emotional_states", [])
        dominant_emotions = []
        if emotional_states:
            # Count emotion frequencies
            emotion_counts = {}
            for emotion in emotional_states:
                if emotion in emotion_counts:
                    emotion_counts[emotion] += 1
                else:
                    emotion_counts[emotion] = 1
            
            # Get the top 3 emotions
            dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            dominant_emotions = [emotion for emotion, count in dominant_emotions]
        
        # Generate summary
        summary = f"Session lasted {duration.total_seconds() // 60} minutes with {interaction_count} interactions. "
        
        if dominant_emotions:
            summary += f"Dominant emotions: {', '.join(dominant_emotions)}. "
        
        # Add condition classifications if available
        condition_classifications = session_data.get("metadata", {}).get("condition_classifications", [])
        if condition_classifications:
            # Get the most recent classification
            latest_classification = condition_classifications[-1]
            summary += f"Psychological assessment indicates {latest_classification}. "
        
        return summary
    
    def _calculate_session_metrics(self, session_data):
        """Calculate metrics for the session
        
        Args:
            session_data (dict): The session data
            
        Returns:
            dict: The session metrics
        """
        metrics = {
            "interaction_count": len(session_data.get("interactions", [])),
            "session_duration": str(datetime.datetime.now() - session_data.get("start_time", datetime.datetime.now())),
            "emotional_states": session_data.get("metadata", {}).get("emotional_states", []),
            "techniques_used": session_data.get("metadata", {}).get("techniques_used", []),
            "condition_classifications": session_data.get("metadata", {}).get("condition_classifications", [])
        }
        
        # Calculate emotional trend
        emotional_states = session_data.get("metadata", {}).get("emotional_states", [])
        if emotional_states:
            # Simplified emotional valence calculation
            positive_emotions = ["joy", "happiness", "excitement", "gratitude", "contentment", "hope"]
            negative_emotions = ["sadness", "anger", "fear", "anxiety", "frustration", "guilt", "shame"]
            
            positive_count = sum(1 for emotion in emotional_states if emotion.lower() in positive_emotions)
            negative_count = sum(1 for emotion in emotional_states if emotion.lower() in negative_emotions)
            
            total_count = len(emotional_states)
            if total_count > 0:
                positive_ratio = positive_count / total_count
                negative_ratio = negative_count / total_count
                
                metrics["emotional_trend"] = {
                    "positive_ratio": positive_ratio,
                    "negative_ratio": negative_ratio,
                    "neutral_ratio": 1 - (positive_ratio + negative_ratio)
                }
        
        # Calculate engagement metrics
        interactions = session_data.get("interactions", [])
        if interactions:
            # Calculate average response time
            response_times = []
            for i in range(1, len(interactions)):
                if "timestamp" in interactions[i] and "timestamp" in interactions[i-1]:
                    response_time = (interactions[i]["timestamp"] - interactions[i-1]["timestamp"]).total_seconds()
                    response_times.append(response_time)
            
            if response_times:
                metrics["average_response_time"] = sum(response_times) / len(response_times)
            
            # Calculate message length trends
            user_message_lengths = [len(interaction.get("user_message", "")) for interaction in interactions]
            if user_message_lengths:
                metrics["average_message_length"] = sum(user_message_lengths) / len(user_message_lengths)
                
                # Check for increasing engagement
                first_half = user_message_lengths[:len(user_message_lengths)//2]
                second_half = user_message_lengths[len(user_message_lengths)//2:]
                
                if first_half and second_half:
                    first_half_avg = sum(first_half) / len(first_half)
                    second_half_avg = sum(second_half) / len(second_half)
                    
                    metrics["engagement_trend"] = "increasing" if second_half_avg > first_half_avg else "decreasing"
        
        # Calculate therapeutic technique effectiveness
        techniques_used = session_data.get("metadata", {}).get("techniques_used", [])
        if techniques_used:
            technique_counts = {}
            for technique in techniques_used:
                technique_counts[technique] = technique_counts.get(technique, 0) + 1
            
            metrics["technique_usage"] = technique_counts
            
            # Calculate effectiveness by emotional state changes after technique use
            if emotional_states and len(emotional_states) == len(techniques_used):
                technique_effectiveness = {}
                
                for i in range(1, len(techniques_used)):
                    technique = techniques_used[i-1]
                    prev_emotion = emotional_states[i-1] if i-1 < len(emotional_states) else None
                    curr_emotion = emotional_states[i] if i < len(emotional_states) else None
                    
                    if prev_emotion and curr_emotion:
                        # Check if emotion improved
                        prev_is_negative = prev_emotion.lower() in negative_emotions
                        curr_is_negative = curr_emotion.lower() in negative_emotions
                        
                        if prev_is_negative and not curr_is_negative:
                            # Emotion improved
                            if technique not in technique_effectiveness:
                                technique_effectiveness[technique] = {"improved": 0, "total": 0}
                            
                            technique_effectiveness[technique]["improved"] += 1
                            technique_effectiveness[technique]["total"] += 1
                        else:
                            # Emotion didn't improve
                            if technique not in technique_effectiveness:
                                technique_effectiveness[technique] = {"improved": 0, "total": 0}
                            
                            technique_effectiveness[technique]["total"] += 1
                
                # Calculate effectiveness percentages
                for technique, stats in technique_effectiveness.items():
                    if stats["total"] > 0:
                        stats["effectiveness_percentage"] = (stats["improved"] / stats["total"]) * 100
                
                metrics["technique_effectiveness"] = technique_effectiveness
        
        return metrics
    
    def _classify_psychological_condition(self, session_data):
        """Classify the psychological condition based on conversation content
        
        Args:
            session_data (dict): The session data
            
        Returns:
            str: The classified condition or None if unable to classify
        """
        try:
            # Extract recent interactions
            interactions = session_data.get("interactions", [])
            if len(interactions) < 3:  # Need at least 3 interactions for meaningful classification
                return None
            
            # Extract user messages and emotion analyses
            user_messages = [interaction.get("user_message", "") for interaction in interactions[-5:]]
            emotion_analyses = [interaction.get("emotion_analysis", {}) for interaction in interactions[-5:]]
            
            # Combine messages for analysis
            combined_text = "\n".join(user_messages)
            
            # Create the prompt for condition classification
            prompt = f"""
            Based on the following user messages and emotional analyses, classify the most likely psychological condition.
            Focus on identifying patterns that might indicate depression, anxiety, bipolar disorder, OCD, or other conditions.
            
            User messages:
            {combined_text}
            
            Emotional analyses:
            {json.dumps(emotion_analyses, indent=2)}
            
            Provide a single classification as one of: "depression", "anxiety", "bipolar", "ocd", "adjustment_disorder", "ptsd", "general_stress", or "unclear".
            
            Classification:
            """
            
            # Use the emotion analyzer's model for classification
            response = self.emotion_analyzer.model.generate_content(prompt)
            
            # Extract the classification
            classification = response.text.strip().lower()
            
            # Validate the classification
            valid_classifications = ["depression", "anxiety", "bipolar", "ocd", "adjustment_disorder", "ptsd", "general_stress", "unclear"]
            if classification in valid_classifications:
                return classification
            else:
                return "unclear"
            
        except Exception as e:
            logger.error(f"Error classifying psychological condition: {e}")
            return None
    
    def _extract_emotional_trends(self, session_data):
        """Extract emotional trends from the session
        
        Args:
            session_data (dict): The session data
            
        Returns:
            list: The emotional trends
        """
        trends = []
        
        # Extract emotional states from interactions
        emotional_states = []
        for interaction in session_data.get("interactions", []):
            if "emotion_analysis" in interaction and "primary_emotion" in interaction["emotion_analysis"]:
                emotional_states.append(interaction["emotion_analysis"]["primary_emotion"])
        
        if emotional_states:
            # Count emotion frequencies
            emotion_counts = {}
            for emotion in emotional_states:
                if emotion in emotion_counts:
                    emotion_counts[emotion] += 1
                else:
                    emotion_counts[emotion] = 1
            
            # Format trends
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
                trends.append(f"{emotion}: {count} times")
        
        return trends
    
    def _extract_progress_indicators(self, session_data):
        """Extract progress indicators from the session
        
        Args:
            session_data (dict): The session data
            
        Returns:
            list: The progress indicators
        """
        indicators = []
        
        # Check for positive emotional shift
        emotional_states = []
        for interaction in session_data.get("interactions", []):
            if "emotion_analysis" in interaction and "primary_emotion" in interaction["emotion_analysis"]:
                emotional_states.append(interaction["emotion_analysis"]["primary_emotion"])
        
        if emotional_states:
            # Simplified emotional valence check
            positive_emotions = ["joy", "happiness", "excitement", "gratitude", "contentment", "hope"]
            negative_emotions = ["sadness", "anger", "fear", "anxiety", "frustration", "guilt", "shame"]
            
            # Check first half vs second half of session
            midpoint = len(emotional_states) // 2
            first_half = emotional_states[:midpoint]
            second_half = emotional_states[midpoint:]
            
            first_half_positive = sum(1 for emotion in first_half if emotion.lower() in positive_emotions)
            second_half_positive = sum(1 for emotion in second_half if emotion.lower() in positive_emotions)
            
            first_half_negative = sum(1 for emotion in first_half if emotion.lower() in negative_emotions)
            second_half_negative = sum(1 for emotion in second_half if emotion.lower() in negative_emotions)
            
            # Check for emotional improvement
            if len(first_half) > 0 and len(second_half) > 0:
                if second_half_positive / len(second_half) > first_half_positive / len(first_half):
                    indicators.append("Increased positive emotions during session")
                
                if second_half_negative / len(second_half) < first_half_negative / len(first_half):
                    indicators.append("Decreased negative emotions during session")
        
        # Check for engagement
        if len(session_data.get("interactions", [])) > 5:
            indicators.append("Sustained engagement throughout session")
        
        return indicators