from datetime import datetime
from bson import ObjectId

class Patient:
    """Patient model for storing patient information
    
    Attributes:
        telegram_id (int): Telegram user ID
        name (str): Patient's name
        condition (str): Mental health condition (depression, bipolar, ocd, unknown)
        registration_date (datetime): Date and time of registration
        metadata (dict): Additional patient metadata
    """
    
    def __init__(self, telegram_id, name, condition, registration_date=None, metadata=None):
        """Initialize a new Patient object
        
        Args:
            telegram_id (int): Telegram user ID
            name (str): Patient's name
            condition (str): Mental health condition
            registration_date (datetime, optional): Registration date and time
            metadata (dict, optional): Additional patient metadata
        """
        self.telegram_id = telegram_id
        self.name = name
        self.condition = condition
        self.registration_date = registration_date or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self):
        """Convert Patient object to dictionary for MongoDB storage
        
        Returns:
            dict: Dictionary representation of the Patient
        """
        return {
            "telegram_id": self.telegram_id,
            "name": self.name,
            "condition": self.condition,
            "registration_date": self.registration_date,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Patient object from a dictionary
        
        Args:
            data (dict): Dictionary containing patient data
            
        Returns:
            Patient: A new Patient object
        """
        return cls(
            telegram_id=data["telegram_id"],
            name=data["name"],
            condition=data["condition"],
            registration_date=data.get("registration_date"),
            metadata=data.get("metadata", {})
        )

class Interaction:
    """Interaction model for storing conversation interactions
    
    Attributes:
        timestamp (datetime): Date and time of the interaction
        user_message (str): Message from the user
        bot_response (str): Response from the bot
        emotion_analysis (dict): Emotional analysis of the user message
        metadata (dict): Additional interaction metadata
    """
    
    def __init__(self, timestamp, user_message, bot_response, emotion_analysis, metadata=None):
        """Initialize a new Interaction object
        
        Args:
            timestamp (datetime): Date and time of the interaction
            user_message (str): Message from the user
            bot_response (str): Response from the bot
            emotion_analysis (dict): Emotional analysis of the user message
            metadata (dict, optional): Additional interaction metadata
        """
        self.timestamp = timestamp
        self.user_message = user_message
        self.bot_response = bot_response
        self.emotion_analysis = emotion_analysis
        self.metadata = metadata or {}
    
    def to_dict(self):
        """Convert Interaction object to dictionary for MongoDB storage
        
        Returns:
            dict: Dictionary representation of the Interaction
        """
        return {
            "timestamp": self.timestamp,
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "emotion_analysis": self.emotion_analysis,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an Interaction object from a dictionary
        
        Args:
            data (dict): Dictionary containing interaction data
            
        Returns:
            Interaction: A new Interaction object
        """
        return cls(
            timestamp=data["timestamp"],
            user_message=data["user_message"],
            bot_response=data["bot_response"],
            emotion_analysis=data["emotion_analysis"],
            metadata=data.get("metadata", {})
        )

class Session:
    """Session model for storing therapy sessions
    
    Attributes:
        patient_id (ObjectId): ID of the patient
        start_time (datetime): Start time of the session
        end_time (datetime): End time of the session
        interactions (list): List of interactions during the session
        summary (str): Summary of the session
        metrics (dict): Session metrics and analytics
    """
    
    def __init__(self, patient_id, start_time, end_time=None, interactions=None, summary=None, metrics=None):
        """Initialize a new Session object
        
        Args:
            patient_id (ObjectId): ID of the patient
            start_time (datetime): Start time of the session
            end_time (datetime, optional): End time of the session
            interactions (list, optional): List of interactions during the session
            summary (str, optional): Summary of the session
            metrics (dict, optional): Session metrics and analytics
        """
        self.patient_id = patient_id
        self.start_time = start_time
        self.end_time = end_time
        self.interactions = interactions or []
        self.summary = summary
        self.metrics = metrics or {}
    
    def to_dict(self):
        """Convert Session object to dictionary for MongoDB storage
        
        Returns:
            dict: Dictionary representation of the Session
        """
        return {
            "patient_id": self.patient_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "interactions": self.interactions,
            "summary": self.summary,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Session object from a dictionary
        
        Args:
            data (dict): Dictionary containing session data
            
        Returns:
            Session: A new Session object
        """
        return cls(
            patient_id=data["patient_id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            interactions=data.get("interactions", []),
            summary=data.get("summary"),
            metrics=data.get("metrics", {})
        )

class Report:
    """Report model for storing generated reports
    
    Attributes:
        patient_id (ObjectId): ID of the patient
        creation_date (datetime): Date and time of report creation
        report_type (str): Type of report (e.g., 'progress', 'assessment')
        content (dict): Report content
        metrics (dict): Report metrics and analytics
    """
    
    def __init__(self, patient_id, creation_date, report_type, content, metrics=None):
        """Initialize a new Report object
        
        Args:
            patient_id (ObjectId): ID of the patient
            creation_date (datetime): Date and time of report creation
            report_type (str): Type of report
            content (dict): Report content
            metrics (dict, optional): Report metrics and analytics
        """
        self.patient_id = patient_id
        self.creation_date = creation_date
        self.report_type = report_type
        self.content = content
        self.metrics = metrics or {}
    
    def to_dict(self):
        """Convert Report object to dictionary for MongoDB storage
        
        Returns:
            dict: Dictionary representation of the Report
        """
        return {
            "patient_id": self.patient_id,
            "creation_date": self.creation_date,
            "report_type": self.report_type,
            "content": self.content,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Report object from a dictionary
        
        Args:
            data (dict): Dictionary containing report data
            
        Returns:
            Report: A new Report object
        """
        return cls(
            patient_id=data["patient_id"],
            creation_date=data["creation_date"],
            report_type=data["report_type"],
            content=data["content"],
            metrics=data.get("metrics", {})
        )