from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from loguru import logger
import datetime
from bson import ObjectId

# Import configuration
import config

# Import core modules
from core.ai_therapist import AITherapist
from core.emotion_analyzer import EmotionAnalyzer
from core.localization import Localization
from core.letting_go import LettingGoTechnique
from core.session_manager import SessionManager
from data.models import Patient, Session, Interaction

# Import reporting module
from reporting.report_generator import ReportGenerator

# Initialize AI components
ai_therapist = AITherapist()
emotion_analyzer = EmotionAnalyzer()

# Initialize localization with default language
localization = Localization(config.DEFAULT_LANGUAGE)

# Initialize letting go technique
letting_go = LettingGoTechnique(localization)

# Session manager will be initialized with the database connection when the bot starts

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
    
    # Set language preference if available
    lang = config.DEFAULT_LANGUAGE
    if patient and 'language' in patient:
        lang = patient['language']
    
    # Update localization
    localization.switch_language(lang)
    
    if patient:
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(localization.get_text('view_progress'), callback_data="view_progress")],
            [InlineKeyboardButton(localization.get_text('get_report'), callback_data="get_report")],
            [InlineKeyboardButton(localization.get_text('letting_go'), callback_data="letting_go")]
        ]
        
        # Add language selection buttons
        language_buttons = []
        for lang_code, lang_name in config.SUPPORTED_LANGUAGES.items():
            language_buttons.append(
                InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
            )
        keyboard.append(language_buttons)
        
        # Send minimal greeting only if not already greeted
        if not context.user_data.get("greeted"):
            await update.message.reply_text(
                localization.get_text('welcome_back', name=patient['name']),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.user_data["greeted"] = True
        
        # Initialize session manager if not already done
        if "session_manager" not in context.bot_data:
            context.bot_data["session_manager"] = SessionManager(db, lang)
            
        # Set greeting flag to ensure welcome message only appears once
        context.user_data["greeted"] = True
        
        # Check for previous session report
        previous_report = context.bot_data["session_manager"].get_previous_session_report(patient["_id"])
        
        # If there's a previous session report, show it
        if previous_report:
            report_message = f"*{localization.get_text('therapeutic_report_title')}*\n\n"
            report_message += f"{localization.get_text('using_since')}: {previous_report['session_date']}\n"
            report_message += f"{localization.get_text('total_sessions')}: {previous_report['interaction_count']}\n\n"
            
            # Add summary
            report_message += f"*{localization.get_text('overall_assessment')}*\n{previous_report['summary']}\n\n"
            
            # Add emotional trends
            if previous_report['emotional_trends']:
                report_message += f"*{localization.get_text('emotional_trends')}*\n"
                for trend in previous_report['emotional_trends'][:3]:  # Show top 3 trends
                    report_message += f"- {trend}\n"
                report_message += "\n"
            
            # Add progress indicators
            if previous_report['progress_indicators']:
                report_message += f"*{localization.get_text('progress_indicators')}*\n"
                for indicator in previous_report['progress_indicators']:
                    report_message += f"- {indicator}\n"
                report_message += "\n"
            
            # Add recommendations
            if previous_report['recommendations']:
                report_message += f"*{localization.get_text('recommendations')}*\n"
                for recommendation in previous_report['recommendations'][:2]:  # Show top 2 recommendations
                    report_message += f"- {recommendation}\n"
            
            # Send the report
            await update.message.reply_text(
                report_message,
                parse_mode="Markdown"
            )
        
        # Start a new session
        session = context.bot_data["session_manager"].start_session(patient["_id"])
        session["user_id"] = user.id
        session["language"] = lang
        context.user_data["session"] = session
        return 'CONVERSATION'
    else:
        # Ask for language preference first
        keyboard = []
        for lang_code, lang_name in config.SUPPORTED_LANGUAGES.items():
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}_new")])
        
        await update.message.reply_text(
            "Please select your preferred language / من فضلك اختر لغتك المفضلة",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return 'LANGUAGE'

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection
    
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
    
    # Extract language code
    if data.startswith("lang_"):
        parts = data.split("_")
        lang_code = parts[1]
        
        # Update localization
        localization.switch_language(lang_code)
        
        # Store language preference
        context.user_data["language"] = lang_code
        
        # Check if this is a new user or existing user changing language
        if len(parts) > 2 and parts[2] == "new":
            # New user, continue with registration
            await query.edit_message_text(
                localization.get_text('welcome', name=query.from_user.first_name)
            )
            return 'REGISTER'
        else:
            # Existing user changing language
            user = update.effective_user
            db = context.bot_data['db']
            
            # Update language preference in database
            db.patients.update_one(
                {"telegram_id": user.id},
                {"$set": {"language": lang_code}}
            )
            
            # Get updated patient data
            patient = db.patients.find_one({"telegram_id": user.id})
            
            # Create keyboard with options for returning users
            keyboard = [
                [InlineKeyboardButton(localization.get_text('view_progress'), callback_data="view_progress")],
                [InlineKeyboardButton(localization.get_text('get_report'), callback_data="get_report")],
                [InlineKeyboardButton(localization.get_text('continue_conversation'), callback_data="continue_conversation")]
            ]
            
            await query.edit_message_text(
                localization.get_text('welcome_back', name=patient['name']),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return 'CONVERSATION'

async def register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user registration
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    # Store user's name
    name = update.message.text
    context.user_data["name"] = name
    
    # Ask about nationality
    await update.message.reply_text(
        localization.get_text('ask_nationality', name=name)
    )
    
    return 'NATIONALITY'

async def nationality_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle nationality collection
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    # Store user's nationality
    nationality = update.message.text
    context.user_data["nationality"] = nationality
    
    # Ask about age
    await update.message.reply_text(
        localization.get_text('ask_age')
    )
    
    return 'AGE'

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle age collection
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    # Store user's age
    try:
        age = int(update.message.text)
        context.user_data["age"] = age
    except ValueError:
        # If not a valid number, store as string
        context.user_data["age"] = update.message.text
    
    # Ask about education
    await update.message.reply_text(
        localization.get_text('ask_education')
    )
    
    return 'EDUCATION'

async def education_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle education collection
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
        
    Returns:
        int: The next conversation state
    """
    # Store user's education
    education = update.message.text
    context.user_data["education"] = education
    
    # Ask about their condition
    conditions_keyboard = [
        [InlineKeyboardButton(localization.get_text('depression'), callback_data="depression")],
        [InlineKeyboardButton(localization.get_text('bipolar'), callback_data="bipolar")],
        [InlineKeyboardButton(localization.get_text('ocd'), callback_data="ocd")],
        [InlineKeyboardButton(localization.get_text('unknown'), callback_data="unknown")]
    ]
    
    await update.message.reply_text(
        localization.get_text('ask_condition'),
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
                "nationality": context.user_data.get("nationality"),
                "age": context.user_data.get("age"),
                "education": context.user_data.get("education"),
                "condition": condition,
                "language": context.user_data.get("language", config.DEFAULT_LANGUAGE)
            }}
        )
        patient_id = existing_patient["_id"]
        logger.info(f"Updated existing patient record for user {user.id}")
    else:
        # Create new patient record
        patient = Patient(
            telegram_id=user.id,
            name=context.user_data["name"],
            nationality=context.user_data.get("nationality"),
            age=context.user_data.get("age"),
            education=context.user_data.get("education"),
            condition=condition,
            language=context.user_data.get("language", config.DEFAULT_LANGUAGE),
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
    
    # Send welcome message with progress tracking button
    message = localization.get_text('registration_complete', condition=condition)
    
    # Add progress tracking button
    keyboard = letting_go.get_progress_keyboard(str(patient_id))
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=keyboard)
    
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
    
    # Check for session end triggers
    end_triggers = ['that\'s it', 'بس كده', 'انتهيت', 'finished']
    if any(trigger in message_text.lower() for trigger in end_triggers):
        return await generate_report_handler(update, context)
    
    # Get patient data
    patient = db.patients.find_one({"telegram_id": user.id})
    if not patient:
        await update.message.reply_text("I couldn't find your records. Let's start over.")
        return await start_handler(update, context)
    
    # Set language preference
    lang = patient.get('language', config.DEFAULT_LANGUAGE)
    localization.switch_language(lang)
    
    # Initialize session manager if not already done
    if "session_manager" not in context.bot_data:
        context.bot_data["session_manager"] = SessionManager(db, lang)
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Analyze emotions in the message
    emotion_analysis = emotion_analyzer.analyze(message_text)
    
    # Get conversation history from session if available
    conversation_history = context.user_data["session"].get("conversation_history", [])
    
    # Get AI therapist response with appropriate language and technique
    response = ai_therapist.generate_response(
        message_text, 
        emotion_analysis, 
        patient["condition"],
        language=lang,
        conversation_history=conversation_history
    )
    
    # Record interaction with metadata about technique used
    metadata = {
        'technique': 'letting_go' if use_letting_go else 'standard',
        'language': lang,
        'user_id': user.id
    }
    
    # Add session_id if it exists
    if "session_id" in context.user_data["session"]:
        metadata['session_id'] = context.user_data["session"]["session_id"]
    
    # Add technique used to session metadata
    if "metadata" not in context.user_data["session"]:
        context.user_data["session"]["metadata"] = {"techniques_used": []}
    if "techniques_used" not in context.user_data["session"]["metadata"]:
        context.user_data["session"]["metadata"]["techniques_used"] = []
    context.user_data["session"]["metadata"]["techniques_used"].append('letting_go' if use_letting_go else 'standard')
    
    # Ensure session has session_id
    if "session_id" not in context.user_data["session"]:
        context.user_data["session"]["session_id"] = str(datetime.now().timestamp())
        
    # Use session manager to add interaction
    context.user_data["session"] = context.bot_data["session_manager"].add_interaction(
        context.user_data["session"],
        message_text,
        response,
        emotion_analysis
    )
    
    # Save session to database periodically
    if len(context.user_data["session"]["interactions"]) % 5 == 0:
        # Create Session object with enhanced fields
        session = Session(
            patient_id=context.user_data["session"]["patient_id"],
            start_time=context.user_data["session"]["start_time"],
            session_id=context.user_data["session"]["session_id"],
            user_id=user.id,
            end_time=datetime.datetime.now(),
            interactions=context.user_data["session"]["interactions"],
            language=lang,
            condition_classification=context.user_data["session"].get("metadata", {}).get("condition_classifications", [])[-1] if context.user_data["session"].get("metadata", {}).get("condition_classifications", []) else None
        )
        db.sessions.insert_one(session.to_dict())
    
    # Create progress tracking button
    keyboard = letting_go.get_progress_keyboard(str(patient["_id"]))
    
    # Send response to user with progress tracking button
    await update.message.reply_text(response, reply_markup=keyboard)
    
    # If using letting go technique and not already in a letting go flow, offer to try it
    if use_letting_go and not context.user_data.get("letting_go_active"):
        # Only suggest letting go technique occasionally to avoid being repetitive
        if len(context.user_data["session"]["interactions"]) % 3 == 0:
            context.user_data["letting_go_active"] = True
            await update.message.reply_text(
                localization.get_text('letting_go_prompt'),
                reply_markup=letting_go.get_prompt_keyboard()
            )
    
    return 'CONVERSATION'

async def generate_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send a session report to the user"""
    user = update.effective_user
    db = context.bot_data['db']
    
    # Get language preference
    lang = config.DEFAULT_LANGUAGE
    patient = db.patients.find_one({"telegram_id": user.id})
    if patient and 'language' in patient:
        lang = patient['language']
    
    # Update localization
    localization.switch_language(lang)
    
    # Generate report
    report = ReportGenerator.generate_session_report(
        context.user_data["session"],
        language=lang
    )
    
    await update.message.reply_text(
        report,
        parse_mode="Markdown"
    )
    
    # End the session
    return await end_conversation_handler(update, context)

async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /report command"""
    return await generate_report_handler(update, context)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command
    
    Args:
        update: The update object from Telegram
        context: The context object from Telegram
    """
    user = update.effective_user
    db = context.bot_data['db']
    
    # Get language preference
    lang = config.DEFAULT_LANGUAGE
    patient = db.patients.find_one({"telegram_id": user.id})
    if patient and 'language' in patient:
        lang = patient['language']
    
    # Update localization
    localization.switch_language(lang)
    
    # Get localized help text
    help_text = localization.get_text('help_text')
    
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
    
    # Get language preference
    lang = config.DEFAULT_LANGUAGE
    patient = db.patients.find_one({"telegram_id": user.id})
    if patient and 'language' in patient:
        lang = patient['language']
    
    # Update localization
    localization.switch_language(lang)
    
    # Initialize session manager if not already done
    if "session_manager" not in context.bot_data:
        context.bot_data["session_manager"] = SessionManager(db, lang)
    
    # Save the current session to database and generate summary
    if "session" in context.user_data:
        # Use session manager to end the session
        session_id = context.bot_data["session_manager"].end_session(context.user_data["session"])
        
        # Generate a brief end-of-session report
        keyboard = [
            [InlineKeyboardButton(localization.get_text('get_report'), callback_data=f"report_{session_id}")],
            [InlineKeyboardButton(localization.get_text('view_progress'), callback_data=f"progress_{patient['_id']}")]
        ]
        
        # Send end message with options to view report or progress
        await update.message.reply_text(
            localization.get_text('end_conversation'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # Clear session data
        context.user_data.clear()
    else:
        await update.message.reply_text(localization.get_text('end_conversation'))
    
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
    
    # Handle language selection
    if data.startswith("lang_"):
        return await language_handler(update, context)
    
    # Handle letting go technique responses
    if data == "letting_go_yes":
        # User wants to try the letting go technique
        patient = db.patients.find_one({"telegram_id": user.id})
        lang = patient.get('language', config.DEFAULT_LANGUAGE)
        localization.switch_language(lang)
        
        # Send the letting go steps
        await query.edit_message_text(letting_go.get_introduction())
        
        # Send the first step
        keyboard = letting_go.get_progress_keyboard(str(patient["_id"]))
        await update.effective_chat.send_message(
            letting_go.get_step_prompt(1),
            reply_markup=keyboard
        )
        
        return 'CONVERSATION'
    
    elif data == "letting_go_no":
        # User doesn't want to try the letting go technique
        patient = db.patients.find_one({"telegram_id": user.id})
        lang = patient.get('language', config.DEFAULT_LANGUAGE)
        localization.switch_language(lang)
        
        # Reset the letting go active flag
        context.user_data["letting_go_active"] = False
        
        # Send acknowledgment
        keyboard = letting_go.get_progress_keyboard(str(patient["_id"]))
        await query.edit_message_text(
            localization.get_text('how_feeling_today', name=patient['name']),
            reply_markup=keyboard
        )
        
        return 'CONVERSATION'
    
    # Handle progress tracking
    elif data.startswith("progress_"):
        # Extract session ID from callback data
        session_id = data.split("_")[1]
        
        patient = db.patients.find_one({"telegram_id": user.id})
        if not patient:
            await query.edit_message_text("I couldn't find your records. Please start a new conversation with /start.")
            return ConversationHandler.END
        
        # Set language preference
        lang = patient.get('language', config.DEFAULT_LANGUAGE)
        localization.switch_language(lang)
        
        # Initialize session manager if not already done
        if "session_manager" not in context.bot_data:
            context.bot_data["session_manager"] = SessionManager(db, lang)
            
        # Set greeting flag to ensure welcome message only appears once
        context.user_data["greeted"] = True
        
        # Get current session data
        session_data = context.user_data.get("session", {})
        
        # Calculate progress metrics
        metrics = letting_go.track_progress(patient, session_data)
        
        # Generate progress message
        progress_message = f"*{localization.get_text('progress_report_title')}*\n\n"
        
        # Add progress percentage
        progress_percentage = metrics.get('progress_percentage', 0)
        progress_bar = "" + "█" * (progress_percentage // 10) + "░" * (10 - progress_percentage // 10)
        progress_message += f"{progress_bar} {progress_percentage}%\n\n"
        
        # Add technique usage
        technique_count = metrics.get('technique_used_count', 0)
        progress_message += f"Letting Go technique used: {technique_count} times\n\n"
        
        # Add emotional trend if available
        recent_emotions = []
        for interaction in session_data.get('interactions', []):
            if "emotion_analysis" in interaction:
                emotion_analysis = interaction["emotion_analysis"]
                if isinstance(emotion_analysis, dict) and "primary_emotion" in emotion_analysis:
                    recent_emotions.append(emotion_analysis["primary_emotion"])
        
        if recent_emotions:
            progress_message += f"{localization.get_text('emotional_trends')}\n"
            for emotion in set(recent_emotions):
                count = recent_emotions.count(emotion)
                progress_message += f"- {emotion.capitalize()}: {count} times\n"
        
        # Add buttons to continue
        keyboard = [
            [InlineKeyboardButton(localization.get_text('continue_conversation'), callback_data="continue_conversation")]
        ]
        
        await query.edit_message_text(
            progress_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
        return 'CONVERSATION'
        
    elif data.startswith("report_"):
        # Extract session ID from callback data
        session_id = data.split("_")[1]
        
        patient = db.patients.find_one({"telegram_id": user.id})
        if not patient:
            await query.edit_message_text("I couldn't find your records. Please start a new conversation with /start.")
            return ConversationHandler.END
        
        # Set language preference
        lang = patient.get('language', config.DEFAULT_LANGUAGE)
        localization.switch_language(lang)
        
        # Initialize session manager if not already done
        if "session_manager" not in context.bot_data:
            context.bot_data["session_manager"] = SessionManager(db, lang)
            
        # Set greeting flag to ensure welcome message only appears once
        context.user_data["greeted"] = True
        
        # Get the session from database
        session = db.sessions.find_one({"_id": ObjectId(session_id)})
        if not session:
            await query.edit_message_text(localization.get_text('report_error'))
            return 'CONVERSATION'
        
        # Generate report message
        report_message = f"*{localization.get_text('therapeutic_report_title')}*\n\n"
        
        # Add session information
        session_date = session.get("end_time", datetime.datetime.now()).strftime("%Y-%m-%d")
        session_duration = str(session.get("end_time", datetime.datetime.now()) - session.get("start_time", datetime.datetime.now()))
        interaction_count = len(session.get("interactions", []))
        
        report_message += f"{localization.get_text('session_date')}: {session_date}\n"
        report_message += f"{localization.get_text('session_duration')}: {session_duration}\n"
        report_message += f"{localization.get_text('interaction_count')}: {interaction_count}\n\n"
        
        # Add summary
        if "summary" in session and session["summary"]:
            report_message += f"*{localization.get_text('summary')}*\n{session['summary']}\n\n"
        
        # Add condition classification if available
        if "condition_classification" in session and session["condition_classification"]:
            report_message += f"*{localization.get_text('condition')}*\n{session['condition_classification'].capitalize()}\n\n"
        
        # Add emotional trends
        emotional_states = []
        for interaction in session.get("interactions", []):
            if "emotion_analysis" in interaction and "primary_emotion" in interaction["emotion_analysis"]:
                emotional_states.append(interaction["emotion_analysis"]["primary_emotion"])
        
        if emotional_states:
            # Count emotion frequencies
            emotion_counts = {}
            for emotion in emotional_states:
                if emotion in emotion_counts:
                    emotion_counts[emotion] += 1
                else:
                    emotion_counts[emotion] = 1
            
            # Format trends
            report_message += f"*{localization.get_text('emotional_trends')}*\n"
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                report_message += f"- {emotion.capitalize()}: {count} times\n"
            report_message += "\n"
        
        # Add recommendations if available
        if "metrics" in session and "recommendations" in session["metrics"]:
            report_message += f"*{localization.get_text('recommendations')}*\n"
            for recommendation in session["metrics"]["recommendations"][:2]:  # Show top 2 recommendations
                report_message += f"- {recommendation}\n"
        
        # Add buttons to start a new conversation
        keyboard = [
            [InlineKeyboardButton(localization.get_text('continue_conversation'), callback_data="continue_conversation")]
        ]
        
        await query.edit_message_text(
            report_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
        return 'CONVERSATION'
    
    elif data in config.SUPPORTED_CONDITIONS or data == "unknown":
        # Handle condition selection
        # Check if user already exists in database
        existing_patient = db.patients.find_one({"telegram_id": user.id})
        
        if existing_patient:
            # Update existing patient record
            db.patients.update_one(
                {"telegram_id": user.id},
                {"$set": {
                    "name": context.user_data["name"],
                    "nationality": context.user_data.get("nationality"),
                    "age": context.user_data.get("age"),
                    "education": context.user_data.get("education"),
                    "condition": data,
                    "language": context.user_data.get("language", config.DEFAULT_LANGUAGE)
                }}
            )
            patient_id = existing_patient["_id"]
            logger.info(f"Updated existing patient record for user {user.id} via callback")
        else:
            # Create new patient record
            patient = Patient(
                telegram_id=user.id,
                name=context.user_data["name"],
                nationality=context.user_data.get("nationality"),
                age=context.user_data.get("age"),
                education=context.user_data.get("education"),
                condition=data,
                language=context.user_data.get("language", config.DEFAULT_LANGUAGE),
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
        
        # Get localized condition name
        condition_key = data if data != "unknown" else "unknown"
        condition_name = localization.get_text(condition_key)
        
        # Send welcome message with progress tracking button
        message = localization.get_text('registration_complete', condition=condition_name)
        
        # Add progress tracking button
        keyboard = letting_go.get_progress_keyboard(str(patient_id))
        
        await query.edit_message_text(message, reply_markup=keyboard)
        
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
        
        await query.edit_message_text(localization.get_text('how_are_you_feeling', name=patient['name']))
        return 'CONVERSATION'
    
    return None