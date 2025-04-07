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

def main():
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