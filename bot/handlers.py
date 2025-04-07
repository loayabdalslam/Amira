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

# Import reporting module
from reporting.report_generator import ReportGenerator

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
        # Create keyboard with options for returning users
        keyboard = [
            [InlineKeyboardButton("View My Progress", callback_data="view_progress")],
            [InlineKeyboardButton("Get Report", callback_data="get_report")],
            [InlineKeyboardButton("Continue Conversation", callback_data="continue_conversation")]
        ]
        
        await update.message.reply_text(
            f"Welcome back, {patient['name']}! What would you like to do today?",
            reply_markup=InlineKeyboardMarkup(keyboard)
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
    
    # Check if user already exists in database
    existing_patient = db.patients.find_one({"telegram_id": user.id})
    
    if existing_patient:
        # Update existing patient record
        db.patients.update_one(
            {"telegram_id": user.id},
            {"$set": {
                "name": context.user_data["name"],
                "condition": condition
            }}
        )
        patient_id = existing_patient["_id"]
        logger.info(f"Updated existing patient record for user {user.id}")
    else:
        # Create new patient record
        patient = Patient(
            telegram_id=user.id,
            name=context.user_data["name"],
            condition=condition,
            registration_date=datetime.datetime.now()
        )
        
        # Save to database
        patient_id = db.patients.insert_one(patient.to_dict()).inserted_id
        logger.info(f"Created new patient record for user {user.id}")
    
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
    user = update.effective_user
    db = context.bot_data['db']
    
    if data in config.SUPPORTED_CONDITIONS or data == "unknown":
        # Handle condition selection
        # Check if user already exists in database
        existing_patient = db.patients.find_one({"telegram_id": user.id})
        
        if existing_patient:
            # Update existing patient record
            db.patients.update_one(
                {"telegram_id": user.id},
                {"$set": {
                    "name": context.user_data["name"],
                    "condition": data
                }}
            )
            patient_id = existing_patient["_id"]
            logger.info(f"Updated existing patient record for user {user.id} via callback")
        else:
            # Create new patient record
            patient = Patient(
                telegram_id=user.id,
                name=context.user_data["name"],
                condition=data,
                registration_date=datetime.datetime.now()
            )
            
            # Save to database
            patient_id = db.patients.insert_one(patient.to_dict()).inserted_id
            logger.info(f"Created new patient record for user {user.id} via callback")
        
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
    
    elif data == "view_progress":
        # Handle view progress button
        patient = db.patients.find_one({"telegram_id": user.id})
        if not patient:
            await query.edit_message_text("I couldn't find your records. Please start a new conversation with /start.")
            return ConversationHandler.END
        
        # Get recent sessions
        recent_sessions = list(db.sessions.find({"patient_id": patient["_id"]}).sort("start_time", -1).limit(5))
        
        # Calculate progress metrics
        total_sessions = db.sessions.count_documents({"patient_id": patient["_id"]})
        total_interactions = 0
        recent_emotions = []
        
        for session in recent_sessions:
            interactions = session.get("interactions", [])
            total_interactions += len(interactions)
            for interaction in interactions:
                if "emotion_analysis" in interaction:
                    recent_emotions.append(interaction["emotion_analysis"])
        
        # Generate progress message
        progress_message = f"📊 *Your Progress Report*\n\n"
        progress_message += f"Total Sessions: {total_sessions}\n"
        progress_message += f"Recent Interactions: {total_interactions}\n\n"
        
        # Add emotional trend if available
        if recent_emotions:
            # Simplified emotion analysis for display
            dominant_emotions = []
            for emotion in recent_emotions:
                if isinstance(emotion, dict) and "dominant_emotion" in emotion:
                    dominant_emotions.append(emotion["dominant_emotion"])
            
            if dominant_emotions:
                progress_message += "Recent Emotional Trends:\n"
                for emotion in set(dominant_emotions):
                    count = dominant_emotions.count(emotion)
                    progress_message += f"- {emotion.capitalize()}: {count} times\n"
        
        # Add engagement info
        progress_message += f"\nYou've been using AMIRA since {patient['registration_date'].strftime('%B %d, %Y')}\n"
        
        # Add buttons for more options
        keyboard = [
            [InlineKeyboardButton("Get Detailed Report", callback_data="get_report")],
            [InlineKeyboardButton("Continue Conversation", callback_data="continue_conversation")]
        ]
        
        await query.edit_message_text(
            progress_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
        return 'CONVERSATION'
    
    elif data == "get_report":
        # Handle get report button
        patient = db.patients.find_one({"telegram_id": user.id})
        if not patient:
            await query.edit_message_text("I couldn't find your records. Please start a new conversation with /start.")
            return ConversationHandler.END
        
        await query.edit_message_text("Generating your therapeutic report... This may take a moment.")
        
        # Initialize report generator
        report_generator = ReportGenerator(db)
        
        # Generate progress report
        report = report_generator.generate_progress_report(patient["_id"])
        
        if report:
            # Format report for Telegram message
            report_content = report.get("content", {})
            
            report_message = f"📝 *Your Therapeutic Report*\n\n"
            
            # Add overall assessment
            if "overall_assessment" in report_content:
                report_message += f"*Overall Assessment:*\n{report_content['overall_assessment']}\n\n"
            
            # Add progress indicators
            if "progress_indicators" in report_content and report_content["progress_indicators"]:
                report_message += "*Progress Indicators:*\n"
                for indicator in report_content["progress_indicators"]:
                    report_message += f"- {indicator}\n"
                report_message += "\n"
            
            # Add recommendations
            if "recommendations" in report_content and report_content["recommendations"]:
                report_message += "*Recommendations:*\n"
                for recommendation in report_content["recommendations"]:
                    report_message += f"- {recommendation}\n"
            
            # Add button to continue conversation
            keyboard = [
                [InlineKeyboardButton("Continue Conversation", callback_data="continue_conversation")]
            ]
            
            await query.edit_message_text(
                report_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "I'm sorry, I couldn't generate a report at this time. Let's continue our conversation instead.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_conversation")]])
            )
        
        return 'CONVERSATION'
    
    elif data == "continue_conversation":
        # Handle continue conversation button
        patient = db.patients.find_one({"telegram_id": user.id})
        if not patient:
            await query.edit_message_text("I couldn't find your records. Please start a new conversation with /start.")
            return ConversationHandler.END
        
        await query.edit_message_text(f"How are you feeling today, {patient['name']}? Tell me what's on your mind.")
        return 'CONVERSATION'
    
    return None