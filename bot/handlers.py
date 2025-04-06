from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from loguru import logger
import datetime

# Import configuration
import config

# Import core modules
from core.ai_therapist import AITherapist
from core.emotion_analyzer import EmotionAnalyzer
from data.models import Patient, Session, Interaction

# Initialize AI components
ai_therapist = AITherapist()
emotion_analyzer = EmotionAnalyzer()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /start command to initiate conversation with the bot
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    db = context.bot_data['db']
    
    # Check if user is already registered
    patient = db.patients.find_one({"telegram_id": user.id})
    
    if patient:
        await update.message.reply_text(
            f"Welcome back, {patient['name']}! How are you feeling today?"
        )
        # Store current session in context
        session = {
            "patient_id": patient["_id"],
            "start_time": datetime.datetime.now(),
            "interactions": []
        }
        context.user_data["session"] = session
        return 'CONVERSATION'
    else:
        await update.message.reply_text(
            f"Hello {user.first_name}! I'm AMIRA, your AI therapeutic assistant. "
            f"To get started, please tell me your full name."
        )
        return 'REGISTER'

async def register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user registration
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    db = context.bot_data['db']
    
    # Store user's name
    name = update.message.text
    context.user_data["name"] = name
    
    # Ask about their condition
    conditions_keyboard = [
        [InlineKeyboardButton("Depression", callback_data="depression")],
        [InlineKeyboardButton("Bipolar Disorder", callback_data="bipolar")],
        [InlineKeyboardButton("OCD", callback_data="ocd")],
        [InlineKeyboardButton("Not sure", callback_data="unknown")]
    ]
    
    await update.message.reply_text(
        f"Thank you, {name}. Which of these conditions best describes what you're experiencing?",
        reply_markup=InlineKeyboardMarkup(conditions_keyboard)
    )
    
    return 'CONDITION'

async def condition_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle condition selection
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    db = context.bot_data['db']
    
    # Get condition from callback data or text message
    condition = update.callback_query.data if update.callback_query else update.message.text.lower()
    
    # Create new patient record
    patient = Patient(
        telegram_id=user.id,
        name=context.user_data["name"],
        condition=condition,
        registration_date=datetime.datetime.now()
    )
    
    # Save to database
    patient_id = db.patients.insert_one(patient.to_dict()).inserted_id
    
    # Create initial session
    session = {
        "patient_id": patient_id,
        "start_time": datetime.datetime.now(),
        "interactions": []
    }
    context.user_data["session"] = session
    
    # Send welcome message
    await update.message.reply_text(
        f"Thank you for sharing that information. I'm here to help you with your {condition}. "
        f"You can talk to me about how you're feeling, and I'll do my best to provide support and guidance. "
        f"What's been on your mind lately?"
    )
    
    return 'CONVERSATION'

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user messages during conversation
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    db = context.bot_data['db']
    message_text = update.message.text
    
    # Analyze emotions in the message
    emotion_analysis = emotion_analyzer.analyze(message_text)
    
    # Get AI therapist response
    patient = db.patients.find_one({"telegram_id": user.id})
    response = ai_therapist.generate_response(message_text, emotion_analysis, patient["condition"])
    
    # Record interaction
    interaction = Interaction(
        timestamp=datetime.datetime.now(),
        user_message=message_text,
        bot_response=response,
        emotion_analysis=emotion_analysis
    )
    
    # Add to current session
    context.user_data["session"]["interactions"].append(interaction.to_dict())
    
    # Save session to database periodically
    if len(context.user_data["session"]["interactions"]) % 5 == 0:
        session = Session(
            patient_id=context.user_data["session"]["patient_id"],
            start_time=context.user_data["session"]["start_time"],
            end_time=datetime.datetime.now(),
            interactions=context.user_data["session"]["interactions"]
        )
        db.sessions.insert_one(session.to_dict())
    
    # Send response to user
    await update.message.reply_text(response)
    
    return 'CONVERSATION'

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
    """
    help_text = (
        "I'm AMIRA, your AI therapeutic assistant. Here's how you can interact with me:\n\n"
        "/start - Start or resume a conversation\n"
        "/help - Show this help message\n"
        "/end - End the current conversation\n\n"
        "You can talk to me about how you're feeling, and I'll do my best to provide support "
        "and guidance based on your specific situation."
    )
    await update.message.reply_text(help_text)

async def end_conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /end command to end the conversation
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: ConversationHandler.END to end the conversation
    """
    user = update.effective_user
    db = context.bot_data['db']
    
    # Save the current session to database
    if "session" in context.user_data:
        session = Session(
            patient_id=context.user_data["session"]["patient_id"],
            start_time=context.user_data["session"]["start_time"],
            end_time=datetime.datetime.now(),
            interactions=context.user_data["session"]["interactions"]
        )
        db.sessions.insert_one(session.to_dict())
        
        # Clear session data
        context.user_data.clear()
    
    await update.message.reply_text(
        "Thank you for talking with me today. I hope our conversation was helpful. "
        "You can start a new conversation anytime by sending /start. Take care!"
    )
    
    return ConversationHandler.END

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callback queries from inline keyboards
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()
    
    # Get the callback data
    data = query.data
    
    if data in config.SUPPORTED_CONDITIONS or data == "unknown":
        # Handle condition selection
        user = update.effective_user
        db = context.bot_data['db']
        
        # Create new patient record
        patient = Patient(
            telegram_id=user.id,
            name=context.user_data["name"],
            condition=data,
            registration_date=datetime.datetime.now()
        )
        
        # Save to database
        patient_id = db.patients.insert_one(patient.to_dict()).inserted_id
        
        # Create initial session
        session = {
            "patient_id": patient_id,
            "start_time": datetime.datetime.now(),
            "interactions": []
        }
        context.user_data["session"] = session
        
        # Send welcome message
        condition_name = {
            "depression": "depression",
            "bipolar": "bipolar disorder",
            "ocd": "obsessive-compulsive disorder",
            "unknown": "concerns"
        }[data]
        
        await query.edit_message_text(
            f"Thank you for sharing that information. I'm here to help you with your {condition_name}. "
            f"You can talk to me about how you're feeling, and I'll do my best to provide support and guidance. "
            f"What's been on your mind lately?"
        )
        
        return 'CONVERSATION'
    
    return None