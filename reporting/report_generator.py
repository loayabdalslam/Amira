import google.generativeai as genai
from loguru import logger
import json
from datetime import datetime

# Import configuration
import config

# No need to import save_report as we're storing directly in MongoDB

class ReportGenerator:
    """Report Generator class for creating detailed patient reports
    
    This class generates comprehensive reports on patient progress,
    emotional state, and treatment effectiveness based on session
    history and interaction data.
    """
    
    def __init__(self, db):
        """Initialize the Report Generator
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        
        # Configure the Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Get the generative model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Report Generator initialized")
    
    def generate_progress_report(self, patient_id):
        """Generate a progress report for a patient
        
        Args:
            patient_id: The ID of the patient
            
        Returns:
            dict: The generated report
        """
        try:
            # Get patient data
            patient = self.db.patients.find_one({"_id": patient_id})
            if not patient:
                logger.error(f"Patient {patient_id} not found")
                return None
            
            # Get session history
            sessions = list(self.db.sessions.find({"patient_id": patient_id}).sort("start_time", -1).limit(10))
            
            # Extract interactions from sessions
            interactions = []
            for session in sessions:
                interactions.extend(session.get("interactions", []))
            
            # Sort interactions by timestamp
            interactions.sort(key=lambda x: x.get("timestamp", datetime.min))
            
            # Generate report using Gemini 2
            report_content = self._generate_report_content(patient, sessions, interactions)
            
            # Create report object
            report = {
                "patient_id": patient_id,
                "creation_date": datetime.now(),
                "report_type": "progress",
                "content": report_content,
                "metrics": self._calculate_metrics(interactions)
            }
            
            # Save report to database only
            report_id = self.db.reports.insert_one(report).inserted_id
            
            logger.info(f"Generated progress report for patient {patient_id}")
            return report
        
        except Exception as e:
            logger.error(f"Error generating progress report: {e}")
            return None
    
    def generate_assessment_report(self, patient_id):
        """Generate a comprehensive assessment report for a patient
        
        Args:
            patient_id: The ID of the patient
            
        Returns:
            dict: The generated report
        """
        try:
            # Get patient data
            patient = self.db.patients.find_one({"_id": patient_id})
            if not patient:
                logger.error(f"Patient {patient_id} not found")
                return None
            
            # Get all session history
            sessions = list(self.db.sessions.find({"patient_id": patient_id}).sort("start_time", 1))
            
            # Extract all interactions
            interactions = []
            for session in sessions:
                interactions.extend(session.get("interactions", []))
            
            # Generate assessment report using Gemini 2
            report_content = self._generate_assessment_content(patient, sessions, interactions)
            
            # Create report object
            report = {
                "patient_id": patient_id,
                "creation_date": datetime.now(),
                "report_type": "assessment",
                "content": report_content,
                "metrics": self._calculate_metrics(interactions, comprehensive=True)
            }
            
            # Save report to database only
            report_id = self.db.reports.insert_one(report).inserted_id
            
            logger.info(f"Generated assessment report for patient {patient_id}")
            return report
        
        except Exception as e:
            logger.error(f"Error generating assessment report: {e}")
            return None
    
    def _generate_report_content(self, patient, sessions, interactions):
        """Generate the content for a progress report using Gemini 2
        
        Args:
            patient (dict): Patient data
            sessions (list): List of session data
            interactions (list): List of interactions
            
        Returns:
            dict: The generated report content
        """
        try:
            # Prepare data for the prompt
            condition = patient.get("condition", "unknown")
            recent_interactions = interactions[-20:] if len(interactions) > 20 else interactions
            
            # Extract emotional states from interactions
            emotional_states = [interaction.get("emotion_analysis", {}) for interaction in recent_interactions]
            
            # Create the prompt for report generation
            prompt = f"""
            Generate a detailed therapeutic progress report for a patient with the following profile:
            
            Patient Condition: {condition}
            Number of Sessions: {len(sessions)}
            Recent Emotional States: {json.dumps(emotional_states, default=str)}
            
            Based on the patient's interaction history and emotional patterns, create a comprehensive progress report that includes:
            
            1. Overall assessment of current psychological state
            2. Progress indicators and improvements observed
            3. Areas of concern or potential setbacks
            4. Patterns in emotional responses and triggers
            5. Effectiveness of therapeutic interventions
            6. Recommendations for continued treatment
            
            Format the response as a JSON object with the following structure:
            {{"overall_assessment": "string",
              "progress_indicators": ["string"],
              "areas_of_concern": ["string"],
              "emotional_patterns": ["string"],
              "intervention_effectiveness": "string",
              "recommendations": ["string"],
              "treatment_stage": "string"
            }}
            
            The treatment_stage should be one of: "early_stage", "progressing", "stable", "improving", "worsening", or "maintenance".
            
            JSON response:
            """
            
            # Generate report from Gemini 2
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
                report_content = json.loads(json_str)
                return report_content
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing report JSON: {e}")
                # Fallback to a basic report
                return {
                    "overall_assessment": "Unable to generate a complete assessment due to processing error.",
                    "progress_indicators": ["Regular engagement with the therapeutic process"],
                    "areas_of_concern": ["Further assessment needed"],
                    "emotional_patterns": ["Varied emotional responses observed"],
                    "intervention_effectiveness": "Requires further evaluation",
                    "recommendations": "Continue with current therapeutic approach while monitoring progress closely.",
                    "treatment_stage": "early_stage"
                }
        
        except Exception as e:
            logger.error(f"Error generating report content: {e}")
            # Return a default report in case of error
            return {
                "overall_assessment": "Unable to generate assessment due to system error.",
                "progress_indicators": ["Continued engagement with therapy"],
                "areas_of_concern": ["System error prevented full analysis"],
                "emotional_patterns": ["Limited data available for analysis"],
                "intervention_effectiveness": "Unable to assess",
                "recommendations": "Continue with current approach and reassess when system is functioning properly.",
                "treatment_stage": "early_stage"
            }
    
    def _generate_assessment_content(self, patient, sessions, interactions):
        """Generate the content for a comprehensive assessment report using Gemini 2
        
        Args:
            patient (dict): Patient data
            sessions (list): List of session data
            interactions (list): List of interactions
            
        Returns:
            dict: The generated assessment content
        """
        try:
            # Prepare data for the prompt
            condition = patient.get("condition", "unknown")
            
            # Sample interactions across the timeline
            sampled_interactions = []
            if len(interactions) <= 30:
                sampled_interactions = interactions
            else:
                # Take samples from beginning, middle, and recent interactions
                sampled_interactions.extend(interactions[:10])  # Beginning
                middle_start = len(interactions) // 2 - 5
                sampled_interactions.extend(interactions[middle_start:middle_start+10])  # Middle
                sampled_interactions.extend(interactions[-10:])  # Recent
            
            # Extract emotional states from sampled interactions
            emotional_states = [interaction.get("emotion_analysis", {}) for interaction in sampled_interactions]
            
            # Create the prompt for assessment generation
            prompt = f"""
            Generate a comprehensive psychological assessment report for a patient with the following profile:
            
            Patient Condition: {condition}
            Number of Sessions: {len(sessions)}
            Duration of Treatment: {(sessions[-1].get('end_time', datetime.now()) - sessions[0].get('start_time', datetime.now())).days} days
            Emotional States Across Treatment: {json.dumps(emotional_states, default=str)}
            
            Based on the patient's interaction history and emotional patterns over time, create a detailed assessment that includes:
            
            1. Comprehensive evaluation of psychological condition and severity
            2. Analysis of symptom progression throughout treatment
            3. Identification of core psychological patterns and themes
            4. Assessment of risk factors and protective factors
            5. Evaluation of treatment response and engagement
            6. Long-term prognosis and treatment recommendations
            7. Specific therapeutic interventions that have shown effectiveness
            
            Format the response as a JSON object with the following structure:
            {{"psychological_evaluation": "string",
              "symptom_progression": "string",
              "core_patterns": ["string"],
              "risk_factors": ["string"],
              "protective_factors": ["string"],
              "treatment_response": "string",
              "prognosis": "string",
              "treatment_recommendations": ["string"],
              "effective_interventions": ["string"],
              "condition_severity": "string",
              "treatment_stage": "string"
            }}
            
            The condition_severity should be one of: "mild", "moderate", "severe", or "in_remission".
            The treatment_stage should be one of: "early_stage", "progressing", "stable", "improving", "worsening", or "maintenance".
            
            JSON response:
            """
            
            # Generate assessment from Gemini 2
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
                assessment_content = json.loads(json_str)
                return assessment_content
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing assessment JSON: {e}")
                # Fallback to a basic assessment
                return {
                    "psychological_evaluation": "Unable to generate a complete evaluation due to processing error.",
                    "symptom_progression": "Insufficient data for comprehensive analysis.",
                    "core_patterns": ["Further assessment needed"],
                    "risk_factors": ["Unable to determine from available data"],
                    "protective_factors": ["Engagement with therapeutic process"],
                    "treatment_response": "Requires further evaluation",
                    "prognosis": "Unclear based on available data",
                    "treatment_recommendations": ["Continue with current therapeutic approach"],
                    "effective_interventions": ["Supportive therapeutic relationship"],
                    "condition_severity": "moderate",
                    "treatment_stage": "early_stage"
                }
        
        except Exception as e:
            logger.error(f"Error generating assessment content: {e}")
            # Return a default assessment in case of error
            return {
                "psychological_evaluation": "Unable to generate evaluation due to system error.",
                "symptom_progression": "Unable to analyze due to system limitations.",
                "core_patterns": ["System error prevented pattern analysis"],
                "risk_factors": ["Unable to determine"],
                "protective_factors": ["Continued engagement with therapy"],
                "treatment_response": "Unable to assess",
                "prognosis": "Unable to determine",
                "treatment_recommendations": ["Continue with current approach"],
                "effective_interventions": ["Unable to determine from available data"],
                "condition_severity": "moderate",
                "treatment_stage": "early_stage"
            }
    
    def _calculate_metrics(self, interactions, comprehensive=False):
        """Calculate metrics based on interactions
        
        Args:
            interactions (list): List of interactions
            comprehensive (bool): Whether to calculate comprehensive metrics
            
        Returns:
            dict: Calculated metrics
        """
        try:
            # Basic metrics
            metrics = {
                "interaction_count": len(interactions),
                "first_interaction": interactions[0]["timestamp"] if interactions else None,
                "last_interaction": interactions[-1]["timestamp"] if interactions else None,
            }
            
            # Calculate emotional metrics
            if interactions:
                # Extract primary emotions
                emotions = [interaction.get("emotion_analysis", {}).get("primary_emotion") 
                           for interaction in interactions 
                           if interaction.get("emotion_analysis", {}).get("primary_emotion")]
                
                # Count emotion frequencies
                emotion_counts = {}
                for emotion in emotions:
                    if emotion in emotion_counts:
                        emotion_counts[emotion] += 1
                    else:
                        emotion_counts[emotion] = 1
                
                # Add to metrics
                metrics["emotion_distribution"] = emotion_counts
                
                # Calculate mood trend
                if comprehensive and len(interactions) >= 5:
                    # Extract emotion intensities
                    intensities = []
                    for interaction in interactions:
                        intensity = interaction.get("emotion_analysis", {}).get("emotion_intensity")
                        if intensity == "low":
                            intensities.append(1)
                        elif intensity == "medium":
                            intensities.append(2)
                        elif intensity == "high":
                            intensities.append(3)
                    
                    # Calculate trend (positive slope = increasing intensity)
                    if intensities:
                        # Simple linear regression
                        n = len(intensities)
                        x = list(range(n))
                        x_mean = sum(x) / n
                        y_mean = sum(intensities) / n
                        
                        numerator = sum((x[i] - x_mean) * (intensities[i] - y_mean) for i in range(n))
                        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
                        
                        slope = numerator / denominator if denominator != 0 else 0
                        metrics["intensity_trend"] = slope
                        
                        # Interpret trend
                        if slope > 0.1:
                            metrics["trend_interpretation"] = "increasing_intensity"
                        elif slope < -0.1:
                            metrics["trend_interpretation"] = "decreasing_intensity"
                        else:
                            metrics["trend_interpretation"] = "stable_intensity"
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {"error": str(e)}