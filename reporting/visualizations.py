import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from loguru import logger

# Import configuration
import config

class Visualizer:
    """Visualizer class for creating data visualizations
    
    This class generates visualizations for patient dashboards,
    including mood trends, engagement metrics, and treatment progress.
    """
    
    def __init__(self, db):
        """Initialize the Visualizer
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Create output directory if it doesn't exist
        os.makedirs('dashboard/static/images', exist_ok=True)
        
        logger.info("Visualizer initialized")
    
    def generate_mood_trend(self, patient_id, days=30):
        """Generate a mood trend visualization
        
        Args:
            patient_id: The ID of the patient
            days (int): Number of days to include in the trend
            
        Returns:
            str: Path to the generated image file
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get sessions in date range
            sessions = list(self.db.sessions.find({
                "patient_id": patient_id,
                "start_time": {"$gte": start_date, "$lte": end_date}
            }).sort("start_time", 1))
            
            # Extract interactions and emotional data
            data = []
            for session in sessions:
                session_date = session.get("start_time").date()
                for interaction in session.get("interactions", []):
                    emotion_analysis = interaction.get("emotion_analysis", {})
                    
                    # Map intensity to numeric value
                    intensity_map = {"low": 1, "medium": 2, "high": 3}
                    intensity = intensity_map.get(
                        emotion_analysis.get("emotion_intensity", "medium"), 2
                    )
                    
                    # Get primary emotion and mood state
                    primary_emotion = emotion_analysis.get("primary_emotion", "neutral")
                    mood_state = emotion_analysis.get("mood_state", "neutral")
                    
                    # Add to data
                    data.append({
                        "date": session_date,
                        "intensity": intensity,
                        "primary_emotion": primary_emotion,
                        "mood_state": mood_state
                    })
            
            # Create DataFrame
            if not data:
                logger.warning(f"No mood data available for patient {patient_id}")
                return self._generate_empty_chart("mood_trend", patient_id)
            
            df = pd.DataFrame(data)
            
            # Aggregate by date
            daily_mood = df.groupby("date").agg({
                "intensity": "mean",
                "primary_emotion": lambda x: x.value_counts().index[0],
                "mood_state": lambda x: x.value_counts().index[0]
            }).reset_index()
            
            # Create visualization
            plt.figure(figsize=(12, 6))
            
            # Plot mood intensity
            ax = sns.lineplot(
                data=daily_mood, x="date", y="intensity",
                marker="o", linewidth=2, color="#3498db"
            )
            
            # Add mood state annotations
            for i, row in daily_mood.iterrows():
                plt.annotate(
                    row["mood_state"],
                    (row["date"], row["intensity"]),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    alpha=0.7
                )
            
            # Set labels and title
            plt.title("Mood Intensity Trend", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Emotional Intensity", fontsize=12)
            
            # Set y-axis ticks
            plt.yticks([1, 2, 3], ["Low", "Medium", "High"])
            
            # Rotate x-axis labels
            plt.xticks(rotation=45)
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            output_path = f"dashboard/static/images/mood_trend_{patient_id}.png"
            plt.savefig(output_path, dpi=100)
            plt.close()
            
            logger.info(f"Generated mood trend visualization for patient {patient_id}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating mood trend: {e}")
            return self._generate_empty_chart("mood_trend", patient_id)
    
    def generate_emotion_distribution(self, patient_id, days=30):
        """Generate an emotion distribution visualization
        
        Args:
            patient_id: The ID of the patient
            days (int): Number of days to include
            
        Returns:
            str: Path to the generated image file
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get sessions in date range
            sessions = list(self.db.sessions.find({
                "patient_id": patient_id,
                "start_time": {"$gte": start_date, "$lte": end_date}
            }))
            
            # Extract emotions
            emotions = []
            for session in sessions:
                for interaction in session.get("interactions", []):
                    emotion = interaction.get("emotion_analysis", {}).get("primary_emotion")
                    if emotion:
                        emotions.append(emotion)
            
            # Create DataFrame
            if not emotions:
                logger.warning(f"No emotion data available for patient {patient_id}")
                return self._generate_empty_chart("emotion_distribution", patient_id)
            
            emotion_counts = pd.Series(emotions).value_counts()
            
            # Create visualization
            plt.figure(figsize=(10, 6))
            
            # Plot emotion distribution
            ax = sns.barplot(
                x=emotion_counts.index,
                y=emotion_counts.values,
                palette="viridis"
            )
            
            # Add count labels
            for i, count in enumerate(emotion_counts.values):
                ax.text(
                    i, count + 0.1, str(count),
                    ha="center", va="bottom",
                    fontsize=10
                )
            
            # Set labels and title
            plt.title("Emotion Distribution", fontsize=16)
            plt.xlabel("Emotion", fontsize=12)
            plt.ylabel("Frequency", fontsize=12)
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha="right")
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            output_path = f"dashboard/static/images/emotion_distribution_{patient_id}.png"
            plt.savefig(output_path, dpi=100)
            plt.close()
            
            logger.info(f"Generated emotion distribution visualization for patient {patient_id}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating emotion distribution: {e}")
            return self._generate_empty_chart("emotion_distribution", patient_id)
    
    def generate_engagement_metrics(self, patient_id, weeks=12):
        """Generate engagement metrics visualization
        
        Args:
            patient_id: The ID of the patient
            weeks (int): Number of weeks to include
            
        Returns:
            str: Path to the generated image file
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks)
            
            # Get sessions in date range
            sessions = list(self.db.sessions.find({
                "patient_id": patient_id,
                "start_time": {"$gte": start_date, "$lte": end_date}
            }).sort("start_time", 1))
            
            # Group sessions by week
            weekly_data = []
            current_date = start_date
            while current_date <= end_date:
                week_start = current_date
                week_end = week_start + timedelta(days=6)
                
                # Count sessions and interactions in this week
                week_sessions = [s for s in sessions if week_start <= s.get("start_time") <= week_end]
                session_count = len(week_sessions)
                
                interaction_count = 0
                for session in week_sessions:
                    interaction_count += len(session.get("interactions", []))
                
                # Calculate average message length
                message_lengths = []
                for session in week_sessions:
                    for interaction in session.get("interactions", []):
                        message = interaction.get("user_message", "")
                        message_lengths.append(len(message))
                
                avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
                
                # Add to weekly data
                weekly_data.append({
                    "week_start": week_start,
                    "session_count": session_count,
                    "interaction_count": interaction_count,
                    "avg_message_length": avg_length
                })
                
                # Move to next week
                current_date += timedelta(days=7)
            
            # Create DataFrame
            df = pd.DataFrame(weekly_data)
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            
            # Create subplot grid
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
            
            # Plot session count
            sns.barplot(
                data=df, x="week_start", y="session_count",
                color="#3498db", ax=ax1
            )
            ax1.set_title("Weekly Sessions", fontsize=14)
            ax1.set_ylabel("Number of Sessions", fontsize=12)
            ax1.set_xlabel("")
            
            # Plot interaction count
            sns.barplot(
                data=df, x="week_start", y="interaction_count",
                color="#2ecc71", ax=ax2
            )
            ax2.set_title("Weekly Interactions", fontsize=14)
            ax2.set_ylabel("Number of Interactions", fontsize=12)
            ax2.set_xlabel("")
            
            # Plot average message length
            sns.lineplot(
                data=df, x="week_start", y="avg_message_length",
                marker="o", color="#e74c3c", ax=ax3
            )
            ax3.set_title("Average Message Length", fontsize=14)
            ax3.set_ylabel("Characters", fontsize=12)
            ax3.set_xlabel("Week Starting", fontsize=12)
            
            # Format x-axis dates
            date_format = lambda x: x.strftime('%b %d')
            ax3.set_xticklabels([date_format(date) for date in df["week_start"]])
            plt.xticks(rotation=45)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save figure
            output_path = f"dashboard/static/images/engagement_metrics_{patient_id}.png"
            plt.savefig(output_path, dpi=100)
            plt.close()
            
            logger.info(f"Generated engagement metrics visualization for patient {patient_id}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating engagement metrics: {e}")
            return self._generate_empty_chart("engagement_metrics", patient_id)
    
    def generate_treatment_progress(self, patient_id):
        """Generate treatment progress visualization
        
        Args:
            patient_id: The ID of the patient
            
        Returns:
            str: Path to the generated image file
        """
        try:
            # Get reports for the patient
            reports = list(self.db.reports.find({
                "patient_id": patient_id
            }).sort("creation_date", 1))
            
            if not reports:
                logger.warning(f"No reports available for patient {patient_id}")
                return self._generate_empty_chart("treatment_progress", patient_id)
            
            # Extract treatment stages and condition severity
            data = []
            for report in reports:
                creation_date = report.get("creation_date")
                content = report.get("content", {})
                
                # Get treatment stage
                treatment_stage = content.get("treatment_stage", "early_stage")
                
                # Get condition severity if available
                condition_severity = content.get("condition_severity", "moderate")
                
                # Add to data
                data.append({
                    "date": creation_date,
                    "treatment_stage": treatment_stage,
                    "condition_severity": condition_severity
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Map treatment stages to numeric values
            stage_map = {
                "early_stage": 1,
                "progressing": 2,
                "stable": 3,
                "improving": 4,
                "worsening": 0,
                "maintenance": 3.5
            }
            df["stage_value"] = df["treatment_stage"].map(stage_map)
            
            # Map condition severity to numeric values
            severity_map = {
                "mild": 1,
                "moderate": 2,
                "severe": 3,
                "in_remission": 0
            }
            df["severity_value"] = df["condition_severity"].map(severity_map)
            
            # Create visualization
            plt.figure(figsize=(12, 6))
            
            # Plot treatment stage
            ax1 = plt.gca()
            ax1.plot(
                df["date"], df["stage_value"],
                marker="o", linewidth=2, color="#3498db",
                label="Treatment Stage"
            )
            
            # Set y-axis ticks for treatment stage
            ax1.set_yticks([0, 1, 2, 3, 4])
            ax1.set_yticklabels(["Worsening", "Early Stage", "Progressing", "Stable", "Improving"])
            ax1.set_ylabel("Treatment Stage", fontsize=12, color="#3498db")
            
            # Create second y-axis for condition severity
            ax2 = ax1.twinx()
            ax2.plot(
                df["date"], df["severity_value"],
                marker="s", linewidth=2, color="#e74c3c", linestyle="--",
                label="Condition Severity"
            )
            
            # Set y-axis ticks for condition severity
            ax2.set_yticks([0, 1, 2, 3])
            ax2.set_yticklabels(["In Remission", "Mild", "Moderate", "Severe"])
            ax2.set_ylabel("Condition Severity", fontsize=12, color="#e74c3c")
            
            # Set labels and title
            plt.title("Treatment Progress Over Time", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            
            # Add legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
            
            # Rotate x-axis labels
            plt.xticks(rotation=45)
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            output_path = f"dashboard/static/images/treatment_progress_{patient_id}.png"
            plt.savefig(output_path, dpi=100)
            plt.close()
            
            logger.info(f"Generated treatment progress visualization for patient {patient_id}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating treatment progress: {e}")
            return self._generate_empty_chart("treatment_progress", patient_id)
    
    def _generate_empty_chart(self, chart_type, patient_id):
        """Generate an empty chart when data is not available
        
        Args:
            chart_type (str): Type of chart
            patient_id: The ID of the patient
            
        Returns:
            str: Path to the generated image file
        """
        plt.figure(figsize=(10, 6))
        
        # Create empty plot with message
        plt.text(
            0.5, 0.5, "Insufficient data available",
            ha="center", va="center", fontsize=14
        )
        
        # Set title based on chart type
        titles = {
            "mood_trend": "Mood Trend",
            "emotion_distribution": "Emotion Distribution",
            "engagement_metrics": "Engagement Metrics",
            "treatment_progress": "Treatment Progress"
        }
        plt.title(titles.get(chart_type, "Chart"), fontsize=16)
        
        # Remove axes
        plt.axis("off")
        
        # Save figure
        output_path = f"dashboard/static/images/{chart_type}_{patient_id}.png"
        plt.savefig(output_path, dpi=100)
        plt.close()
        
        return output_path