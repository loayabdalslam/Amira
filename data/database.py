from pymongo import MongoClient
from loguru import logger
import os

# Import configuration
import config

def initialize_database():
    """Initialize the MongoDB database connection
    
    Returns:
        pymongo.database.Database: MongoDB database object
    """
    try:
        # Connect to MongoDB
        client = MongoClient(config.MONGODB_URI)
        db = client[config.MONGODB_DB_NAME]
        
        # Create necessary collections if they don't exist
        if 'patients' not in db.list_collection_names():
            db.create_collection('patients')
            logger.info("Created 'patients' collection")
        
        if 'sessions' not in db.list_collection_names():
            db.create_collection('sessions')
            logger.info("Created 'sessions' collection")
        
        if 'reports' not in db.list_collection_names():
            db.create_collection('reports')
            logger.info("Created 'reports' collection")
        
        # Create indexes for better query performance
        db.patients.create_index('telegram_id', unique=True)
        db.sessions.create_index('patient_id')
        db.reports.create_index([('patient_id', 1), ('creation_date', -1)])
        
        logger.info(f"Connected to MongoDB database: {config.MONGODB_DB_NAME}")
        return db
    
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

def save_patient_data(patient_id, data):
    """Save patient data to the file system
    
    Args:
        patient_id: The ID of the patient
        data (dict): The data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create patient directory if it doesn't exist
        patient_dir = os.path.join(config.PATIENT_DATA_DIR, str(patient_id))
        os.makedirs(patient_dir, exist_ok=True)
        
        # Save data to file
        file_path = os.path.join(patient_dir, 'patient_data.json')
        with open(file_path, 'w') as f:
            import json
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved patient data for patient {patient_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving patient data: {e}")
        return False

def save_session_data(patient_id, session_id, data):
    """Save session data to the file system
    
    Args:
        patient_id: The ID of the patient
        session_id: The ID of the session
        data (dict): The session data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create patient directory if it doesn't exist
        patient_dir = os.path.join(config.PATIENT_DATA_DIR, str(patient_id))
        os.makedirs(patient_dir, exist_ok=True)
        
        # Create sessions directory if it doesn't exist
        sessions_dir = os.path.join(patient_dir, 'sessions')
        os.makedirs(sessions_dir, exist_ok=True)
        
        # Save data to file
        file_path = os.path.join(sessions_dir, f'{session_id}.json')
        with open(file_path, 'w') as f:
            import json
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved session data for patient {patient_id}, session {session_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving session data: {e}")
        return False

def save_report(patient_id, report_id, report_data):
    """Save a generated report to the file system
    
    Args:
        patient_id: The ID of the patient
        report_id: The ID of the report
        report_data (dict): The report data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create patient directory if it doesn't exist
        patient_dir = os.path.join(config.PATIENT_DATA_DIR, str(patient_id))
        os.makedirs(patient_dir, exist_ok=True)
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(patient_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save data to file
        file_path = os.path.join(reports_dir, f'{report_id}.json')
        with open(file_path, 'w') as f:
            import json
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Saved report for patient {patient_id}, report {report_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        return False