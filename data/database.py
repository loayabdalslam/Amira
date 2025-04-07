from pymongo import MongoClient
from loguru import logger

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

# File system operations removed as per requirements
# All patient data is now stored directly in MongoDB

# File system operations for session data removed
# All session data is now stored directly in MongoDB

# File system operations for report data removed
# All report data is now stored directly in MongoDB