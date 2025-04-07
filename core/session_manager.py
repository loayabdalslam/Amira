from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
from data.database import Database
from core.localization import Localization
from bson import ObjectId

class SessionManager:
    def __init__(self, db, language='en'):
        self.db = db
        self.localization = Localization(language)
    
    def start_session(self, patient_id) -> Dict:
        """Start a new session for a patient
        
        Args:
            patient_id: The patient's ID
            
        Returns:
            Dict: The session object
        """
        session = {
            'patient_id': patient_id,
            'session_id': str(datetime.now().timestamp()),
            'start_time': datetime.now(),
            'interactions': [],
            'metadata': {'techniques_used': []},
            'conversation_history': []
        }
        return session
    
    def create_session(self, user_id: int, language: str = 'en') -> Dict:
        """Create a new session for a user"""
        session = {
            'user_id': user_id,
            'session_id': str(datetime.now().timestamp()),
            'start_time': datetime.now(),
            'language': language,
            'messages': [],
            'emotional_states': [],
            'progress': {},
            'diagnosis_progress': {}
        }
        
        self.db.save_session(session)
        return session
    
    def add_message(self, session_id: str, message: Dict) -> None:
        """Add a message to the session history"""
        message['timestamp'] = datetime.now()
        self.db.add_message_to_session(session_id, message)
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get the complete conversation history for a session"""
        return self.db.get_session_messages(session_id)
        
    def add_interaction(self, session, user_message, bot_response, emotion_analysis) -> Dict:
        """Add an interaction to the session and update conversation history
        
        Args:
            session: The current session object
            user_message: The message from the user
            bot_response: The response from the bot
            emotion_analysis: Emotional analysis of the user message
            
        Returns:
            Dict: The updated session object
        """
        # Create interaction object
        interaction = {
            'timestamp': datetime.now(),
            'user_message': user_message,
            'bot_response': bot_response,
            'emotion_analysis': emotion_analysis
        }
        
        # Add to interactions list
        if 'interactions' not in session:
            session['interactions'] = []
        session['interactions'].append(interaction)
        
        # Update conversation history
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        session['conversation_history'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now()
        })
        session['conversation_history'].append({
            'role': 'assistant',
            'content': bot_response,
            'timestamp': datetime.now()
        })
        
        # Update emotional state if available
        if emotion_analysis and 'dominant_emotion' in emotion_analysis:
            self.update_emotional_state(
                session.get('session_id', str(datetime.now().timestamp())),
                emotion_analysis['dominant_emotion'],
                emotion_analysis.get('intensity', 0.5)
            )
            
            # Update diagnosis progress based on emotion
            if 'condition' in session:
                progress = self._calculate_progress(session['condition'], emotion_analysis)
                self.update_diagnosis_progress(
                    session.get('session_id', str(datetime.now().timestamp())),
                    session['condition'],
                    progress
                )
        
        return session
        
    def _calculate_progress(self, condition, emotion_analysis):
        """Calculate progress for a condition based on emotional analysis
        
        Args:
            condition: The psychological condition
            emotion_analysis: Emotional analysis data
            
        Returns:
            float: Progress value between 0 and 1
        """
        # Simple implementation - can be enhanced with more sophisticated algorithms
        positive_emotions = ['joy', 'happiness', 'calm', 'contentment', 'relief']
        if emotion_analysis and 'dominant_emotion' in emotion_analysis:
            if emotion_analysis['dominant_emotion'].lower() in positive_emotions:
                return 0.1  # Small progress for positive emotions
        return 0.05  # Minimal progress for other emotions
    
    def update_emotional_state(self, session_id: str, emotion: str, intensity: float) -> None:
        """Update the emotional state tracking for the session"""
        emotional_state = {
            'emotion': emotion,
            'intensity': intensity,
            'timestamp': datetime.now()
        }
        self.db.update_session_emotional_state(session_id, emotional_state)
    
    def update_diagnosis_progress(self, session_id: str, diagnosis: str, progress: float) -> None:
        """Update the progress for a specific diagnosis"""
        self.db.update_diagnosis_progress(session_id, diagnosis, progress)
    
    def get_diagnosis_progress(self, user_id: int) -> Dict:
        """Get the progress for all diagnoses for a user"""
        return self.db.get_user_diagnosis_progress(user_id)
    
    def get_session_language(self, session_id: str) -> str:
        """Get the language setting for a session"""
        session = self.db.get_session(session_id)
        return session.get('language', 'en')
    
    def set_session_language(self, session_id: str, language: str) -> None:
        """Set the language for a session"""
        self.db.update_session_language(session_id, language)
        self.localization.switch_language(language)
    
    def get_session_summary(self, session_id: str, language: str = None) -> Dict:
        """Get a summary of the session including progress and emotional states"""
        session = self.db.get_session(session_id)
        if not session:
            return None
            
        if language:
            self.localization.switch_language(language)
            
        summary = {
            'start_time': session['start_time'],
            'message_count': len(session.get('messages', [])),
            'emotional_states': session.get('emotional_states', []),
            'progress': session.get('progress', {}),
            'diagnosis_progress': session.get('diagnosis_progress', {})
        }
        
        # Localize summary if language is Arabic
        if language == 'ar':
            summary = self._localize_summary(summary)
            
        return summary
    
    def _localize_summary(self, summary: Dict) -> Dict:
        """Localize the summary content to Arabic"""
        localized = summary.copy()
        
        # Localize emotional states
        if 'emotional_states' in localized:
            for state in localized['emotional_states']:
                state['emotion'] = self.localization.get_text(state['emotion'])
                
        # Localize progress metrics
        if 'progress' in localized:
            localized_progress = {}
            for key, value in localized['progress'].items():
                localized_key = self.localization.get_text(key)
                localized_progress[localized_key] = value
            localized['progress'] = localized_progress
            
        return localized
        
    def end_session(self, session) -> str:
        """End a session and save it to the database
        
        Args:
            session: The session object to end
            
        Returns:
            str: The session ID
        """
        # Set end time
        session['end_time'] = datetime.now()
        
        # Calculate session duration
        start_time = session.get('start_time', datetime.now())
        session['duration'] = (session['end_time'] - start_time).total_seconds() / 60  # in minutes
        
        # Generate simple summary
        session['summary'] = self._generate_session_summary(session)
        
        # Save to database
        if 'session_id' in session:
            self.db.sessions.update_one(
                {'session_id': session['session_id']},
                {'$set': session},
                upsert=True
            )
            return session['session_id']
        else:
            # If no session_id, create one
            session['session_id'] = str(datetime.now().timestamp())
            self.db.sessions.insert_one(session)
            return session['session_id']
    
    def _generate_session_summary(self, session) -> str:
        """Generate a simple summary of the session
        
        Args:
            session: The session object
            
        Returns:
            str: A summary of the session
        """
        # Get language
        lang = session.get('language', 'en')
        self.localization.switch_language(lang)
        
        # Count interactions
        interaction_count = len(session.get('interactions', []))
        
        # Determine dominant emotions
        emotions = []
        for interaction in session.get('interactions', []):
            if 'emotion_analysis' in interaction and 'dominant_emotion' in interaction['emotion_analysis']:
                emotions.append(interaction['emotion_analysis']['dominant_emotion'].lower())
        
        # Count emotion frequencies
        emotion_counts = {}
        for emotion in emotions:
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1
            else:
                emotion_counts[emotion] = 1
        
        # Get top emotions
        top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate summary text
        if lang == 'ar':
            summary = f"جلسة مع {interaction_count} تفاعلات. "
            if top_emotions:
                summary += "المشاعر السائدة: "
                summary += ", ".join([self.localization.get_text(emotion) for emotion, _ in top_emotions])
        else:
            summary = f"Session with {interaction_count} interactions. "
            if top_emotions:
                summary += "Dominant emotions: "
                summary += ", ".join([emotion for emotion, _ in top_emotions])
        
        return summary
        
    def get_previous_session_report(self, patient_id):
        """Get a report of the previous session for a patient
        
        Args:
            patient_id: The patient's ID
            
        Returns:
            dict: Report data or None if no previous sessions
        """
        # Find the most recent session for this patient
        previous_session = self.db.sessions.find_one(
            {'patient_id': patient_id},
            sort=[('start_time', -1)]
        )
        
        if not previous_session:
            return None
        
        # Get language
        lang = previous_session.get('language', 'en')
        self.localization.switch_language(lang)
        
        # Format date
        session_date = previous_session.get('start_time', datetime.now()).strftime('%Y-%m-%d')
        
        # Count interactions
        interaction_count = len(previous_session.get('interactions', []))
        
        # Generate report
        report = {
            'session_date': session_date,
            'interaction_count': interaction_count,
            'summary': previous_session.get('summary', self.localization.get_text('no_summary_available')),
            'emotional_trends': self._extract_emotional_trends(previous_session, lang),
            'progress_indicators': self._extract_progress_indicators(previous_session, lang),
            'recommendations': self._generate_recommendations(previous_session, lang)
        }
        
        return report
    
    def _extract_emotional_trends(self, session, lang):
        """Extract emotional trends from a session
        
        Args:
            session: The session object
            lang: Language code
            
        Returns:
            list: List of emotional trend descriptions
        """
        trends = []
        emotions = []
        
        # Extract emotions from interactions
        for interaction in session.get('interactions', []):
            if 'emotion_analysis' in interaction and 'dominant_emotion' in interaction['emotion_analysis']:
                emotions.append(interaction['emotion_analysis']['dominant_emotion'].lower())
        
        if not emotions:
            return trends
        
        # Count emotion frequencies
        emotion_counts = {}
        for emotion in emotions:
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1
            else:
                emotion_counts[emotion] = 1
        
        # Get top emotions
        top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate trend descriptions
        for emotion, count in top_emotions:
            percentage = int((count / len(emotions)) * 100)
            if lang == 'ar':
                trends.append(f"{self.localization.get_text(emotion)}: {percentage}% من التفاعلات")
            else:
                trends.append(f"{emotion.capitalize()}: {percentage}% of interactions")
        
        return trends
    
    def _extract_progress_indicators(self, session, lang):
        """Extract progress indicators from a session
        
        Args:
            session: The session object
            lang: Language code
            
        Returns:
            list: List of progress indicator descriptions
        """
        indicators = []
        
        # Check for techniques used
        techniques = session.get('metadata', {}).get('techniques_used', [])
        letting_go_count = techniques.count('letting_go')
        
        if letting_go_count > 0:
            if lang == 'ar':
                indicators.append(f"استخدمت تقنية الترك {letting_go_count} مرات")
            else:
                indicators.append(f"Used Letting Go technique {letting_go_count} times")
        
        # Check for emotional shifts
        emotions = []
        for interaction in session.get('interactions', []):
            if 'emotion_analysis' in interaction and 'dominant_emotion' in interaction['emotion_analysis']:
                emotions.append(interaction['emotion_analysis']['dominant_emotion'].lower())
        
        if len(emotions) >= 2:
            first_half = emotions[:len(emotions)//2]
            second_half = emotions[len(emotions)//2:]
            
            # Check if emotions improved in second half
            positive_emotions = ['joy', 'happiness', 'calm', 'contentment', 'relief']
            negative_emotions = ['anger', 'fear', 'sadness', 'disgust', 'anxiety', 'stress']
            
            first_half_negative = sum(1 for e in first_half if e in negative_emotions)
            second_half_negative = sum(1 for e in second_half if e in negative_emotions)
            
            first_half_positive = sum(1 for e in first_half if e in positive_emotions)
            second_half_positive = sum(1 for e in second_half if e in positive_emotions)
            
            if second_half_positive > first_half_positive:
                if lang == 'ar':
                    indicators.append("زيادة في المشاعر الإيجابية خلال الجلسة")
                else:
                    indicators.append("Increase in positive emotions during the session")
            
            if second_half_negative < first_half_negative:
                if lang == 'ar':
                    indicators.append("انخفاض في المشاعر السلبية خلال الجلسة")
                else:
                    indicators.append("Decrease in negative emotions during the session")
        
        return indicators
    
    def _generate_recommendations(self, session, lang):
        """Generate recommendations based on session data
        
        Args:
            session: The session object
            lang: Language code
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        # Check for techniques used
        techniques = session.get('metadata', {}).get('techniques_used', [])
        letting_go_count = techniques.count('letting_go')
        
        if letting_go_count == 0:
            if lang == 'ar':
                recommendations.append("جرب تقنية الترك للمساعدة في التعامل مع المشاعر السلبية")
            else:
                recommendations.append("Try the Letting Go technique to help deal with negative emotions")
        
        # Check for emotional patterns
        emotions = []
        for interaction in session.get('interactions', []):
            if 'emotion_analysis' in interaction and 'dominant_emotion' in interaction['emotion_analysis']:
                emotions.append(interaction['emotion_analysis']['dominant_emotion'].lower())
        
        if emotions:
            # Check for persistent negative emotions
            negative_emotions = ['anger', 'fear', 'sadness', 'disgust', 'anxiety', 'stress']
            negative_count = sum(1 for e in emotions if e in negative_emotions)
            
            if negative_count > len(emotions) * 0.7:  # More than 70% negative
                if lang == 'ar':
                    recommendations.append("تمارين التنفس العميق يمكن أن تساعد في تقليل المشاعر السلبية المستمرة")
                else:
                    recommendations.append("Deep breathing exercises can help reduce persistent negative emotions")
        
        return recommendations