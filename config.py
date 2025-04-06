import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'amira_db')

# Application Configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Patient Data Configuration
PATIENT_DATA_DIR = os.getenv('PATIENT_DATA_DIR', 'patient_data')

# Supported Mental Health Conditions
SUPPORTED_CONDITIONS = [
    'depression',
    'bipolar',
    'ocd'
]

# Therapy Session Configuration
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '1800'))  # 30 minutes in seconds

# Report Generation Configuration
REPORT_TEMPLATE_DIR = os.getenv('REPORT_TEMPLATE_DIR', 'report_templates')