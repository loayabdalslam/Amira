import os
import logging
from loguru import logger

# Import configuration
import config

# Import bot module
from bot.bot import setup_bot

# Import database module
from data.database import initialize_database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)

# Create necessary directories if they don't exist
def setup_directories():
    # Create patient data directory
    os.makedirs(config.PATIENT_DATA_DIR, exist_ok=True)
    logger.info(f"Created patient data directory: {config.PATIENT_DATA_DIR}")
    
    # Create report template directory
    os.makedirs(config.REPORT_TEMPLATE_DIR, exist_ok=True)
    logger.info(f"Created report template directory: {config.REPORT_TEMPLATE_DIR}")

def main():
    # Setup necessary directories
    setup_directories()
    
    # Initialize database connection
    db = initialize_database()
    logger.info("Database connection initialized")
    
    # Setup and run the Telegram bot
    bot = setup_bot(db)
    logger.info("Starting Telegram bot")
    bot.run_polling()
    
if __name__ == "__main__":
    logger.info("Starting AMIRA - AI Mental Health Therapeutic Assistant")
    main()