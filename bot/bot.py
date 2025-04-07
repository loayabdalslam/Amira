from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from loguru import logger

# Import configuration
import config

# Import handlers
from bot.handlers import (
    start_handler, help_handler, message_handler, 
    register_handler, condition_handler, end_conversation_handler,
    callback_query_handler,language_handler, nationality_handler, age_handler, education_handler
)

def setup_bot(db):
    """Setup and configure the Telegram bot
    
    Args:
        db: MongoDB database connection
        
    Returns:
        telegram.ext.Application: Configured bot application
    """
    # Create the Application
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
    
    # Add conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_handler)],
        states={
            'LANGUAGE': [
                CallbackQueryHandler(language_handler)
            ],
            'REGISTER': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register_handler)
            ],
            'NATIONALITY': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nationality_handler)
            ],
            'AGE': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, age_handler)
            ],
            'EDUCATION': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, education_handler)
            ],
            'CONDITION': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, condition_handler),
                CallbackQueryHandler(callback_query_handler)
            ],
            'CONVERSATION': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler),
                CallbackQueryHandler(callback_query_handler)
            ],
        },
        fallbacks=[CommandHandler('end', end_conversation_handler)],
    )
    
    # Add handlers to the application
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_handler))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    
    # Store database connection in application
    application.bot_data['db'] = db
    
    logger.info("Telegram bot configured successfully")
    return application