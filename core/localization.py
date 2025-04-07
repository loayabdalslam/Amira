\"""Localization module for AMIRA

This module provides multilingual support for the AMIRA bot,
currently supporting English and Arabic (Egyptian dialect).
"""

class Localization:
    """Localization class for handling multilingual support
    
    This class provides translations for all user-facing messages in the AMIRA bot.
    Currently supports English and Arabic (Egyptian dialect).
    """
    
    # Available languages
    ENGLISH = 'en'
    ARABIC = 'ar'
    
    # Default language
    DEFAULT_LANGUAGE = ENGLISH
    
    def __init__(self, language=DEFAULT_LANGUAGE):
        """Initialize the Localization object with a language
        
        Args:
            language (str, optional): Language code ('en' or 'ar')
        """
        self.language = language if language in [self.ENGLISH, self.ARABIC] else self.DEFAULT_LANGUAGE
    
    def get_text(self, key, **kwargs):
        """Get localized text for a given key
        
        Args:
            key (str): The text key to translate
            **kwargs: Format parameters for the text
            
        Returns:
            str: The localized text
        """
        if self.language == self.ARABIC:
            text = self.ARABIC_TEXTS.get(key, self.ENGLISH_TEXTS.get(key, key))
        else:
            text = self.ENGLISH_TEXTS.get(key, key)
        
        # Format the text with provided parameters
        if kwargs:
            text = text.format(**kwargs)
        
        return text
    
    def switch_language(self, language):
        """Switch the current language
        
        Args:
            language (str): Language code ('en' or 'ar')
        """
        if language in [self.ENGLISH, self.ARABIC]:
            self.language = language
    
    # English texts
    ENGLISH_TEXTS = {
        # Welcome and registration
        'welcome': "Hello {name}! I'm AMIRA, your AI therapeutic assistant. To get started, please tell me your full name.",
        'welcome_back': "Welcome back, {name}! What would you like to do today?",
        'ask_nationality': "Thank you, {name}. Could you please tell me your nationality?",
        'ask_age': "Thank you. Now, could you please tell me your age?",
        'ask_education': "Great! Finally, could you share your level of education or what you're currently studying?",
        'ask_condition': "Thank you for sharing that information. Which of these conditions best describes what you're experiencing?",
        'registration_complete': "Thank you for sharing your information. I'm here to help you with your {condition}. You can talk to me about how you're feeling, and I'll do my best to provide support and guidance. What's been on your mind lately?",
        
        # Buttons and options
        'view_progress': "View My Progress",
        'get_report': "Get Report",
        'continue_conversation': "Continue Conversation",
        'calculate_progress': "Calculate My Progress",
        
        # Conditions
        'depression': "Depression",
        'bipolar': "Bipolar Disorder",
        'ocd': "OCD",
        'unknown': "Not sure",
        
        # Help
        'help_text': "I'm AMIRA, your AI therapeutic assistant. Here's how you can interact with me:\n\n"
                    "/start - Start or resume a conversation\n"
                    "/help - Show this help message\n"
                    "/end - End the current conversation\n\n"
                    "You can talk to me about how you're feeling, and I'll do my best to provide support "
                    "and guidance based on your specific situation.",
        
        # End conversation
        'end_conversation': "Thank you for talking with me today. I hope our conversation was helpful. "
                           "You can start a new conversation anytime by sending /start. Take care!",
        
        # Progress and reports
        'progress_report_title': "📊 Your Progress Report",
        'total_sessions': "Total Sessions: {count}",
        'recent_interactions': "Recent Interactions: {count}",
        'emotional_trends': "Recent Emotional Trends:",
        'using_since': "You've been using AMIRA since {date}",
        'generating_report': "Generating your therapeutic report... This may take a moment.",
        'therapeutic_report_title': "📝 Your Therapeutic Report",
        'overall_assessment': "Overall Assessment:",
        'progress_indicators': "Progress Indicators:",
        'recommendations': "Recommendations:",
        'report_error': "I'm sorry, I couldn't generate a report at this time. Let's continue our conversation instead.",
        'how_feeling_today': "How are you feeling today, {name}? Tell me what's on your mind.",
        
        # Letting Go Technique
        'letting_go_intro': "I'd like to introduce you to the Letting Go technique by David R. Hawkins. This technique helps you release negative emotions by acknowledging and accepting them, rather than suppressing or expressing them.",
        'letting_go_step1': "Step 1: Identify the emotion you're feeling right now. Can you name it?",
        'letting_go_step2': "Step 2: Allow yourself to fully feel this emotion without judgment. Where do you feel it in your body?",
        'letting_go_step3': "Step 3: Ask yourself if you're willing to let go of this feeling, even just a little bit.",
        'letting_go_step4': "Step 4: Ask yourself when you could let it go. Could you let it go now?",
        'letting_go_prompt': "Would you like to try the Letting Go technique with what you're feeling right now?",
        'letting_go_yes': "Yes, I'd like to try",
        'letting_go_no': "Not right now",
    }
    
    # Arabic texts (Egyptian dialect)
    ARABIC_TEXTS = {
        # Welcome and registration
        'welcome': "أهلا {name}! أنا أميرة، مساعدتك العلاجية الذكية. للبدء، من فضلك قولي اسمك الكامل.",
        'welcome_back': "أهلا بعودتك، {name}! ماذا تريد أن تفعل اليوم؟",
        'ask_nationality': "شكرا، {name}. ممكن تقولي جنسيتك؟",
        'ask_age': "شكرا. دلوقتي، ممكن تقولي عندك كام سنة؟",
        'ask_education': "تمام! أخيرا، ممكن تشاركني مستوى تعليمك أو إيه بتدرس حاليا؟",
        'ask_condition': "شكرا لمشاركة هذه المعلومات. أي من هذه الحالات تصف ما تشعر به؟",
        'registration_complete': "شكرا لمشاركة معلوماتك. أنا هنا لمساعدتك مع {condition}. يمكنك التحدث معي عن شعورك، وسأبذل قصارى جهدي لتقديم الدعم والتوجيه. ما الذي يشغل بالك مؤخرا؟",
        
        # Buttons and options
        'view_progress': "عرض تقدمي",
        'get_report': "الحصول على تقرير",
        'continue_conversation': "متابعة المحادثة",
        'calculate_progress': "حساب تقدمي",
        
        # Conditions
        'depression': "الاكتئاب",
        'bipolar': "الاضطراب ثنائي القطب",
        'ocd': "الوسواس القهري",
        'unknown': "مش متأكد",
        
        # Help
        'help_text': "أنا أميرة، مساعدتك العلاجية الذكية. إليك كيفية التفاعل معي:\n\n"
                    "/start - بدء أو استئناف محادثة\n"
                    "/help - عرض رسالة المساعدة هذه\n"
                    "/end - إنهاء المحادثة الحالية\n\n"
                    "يمكنك التحدث معي عن شعورك، وسأبذل قصارى جهدي لتقديم الدعم "
                    "والتوجيه بناءً على وضعك المحدد.",
        
        # End conversation
        'end_conversation': "شكرا للتحدث معي اليوم. آمل أن تكون محادثتنا مفيدة. "
                           "يمكنك بدء محادثة جديدة في أي وقت بإرسال /start. اعتني بنفسك!",
        
        # Progress and reports
        'progress_report_title': "📊 تقرير تقدمك",
        'total_sessions': "إجمالي الجلسات: {count}",
        'recent_interactions': "التفاعلات الأخيرة: {count}",
        'emotional_trends': "اتجاهات المشاعر الأخيرة:",
        'using_since': "أنت تستخدم أميرة منذ {date}",
        'generating_report': "جاري إنشاء تقريرك العلاجي... قد يستغرق هذا لحظة.",
        'therapeutic_report_title': "📝 تقريرك العلاجي",
        'overall_assessment': "التقييم العام:",
        'progress_indicators': "مؤشرات التقدم:",
        'recommendations': "التوصيات:",
        'report_error': "آسفة، لم أتمكن من إنشاء تقرير في هذا الوقت. دعنا نواصل محادثتنا بدلاً من ذلك.",
        'how_feeling_today': "كيف تشعر اليوم، {name}؟ أخبرني بما يدور في ذهنك.",
        
        # Letting Go Technique
        'letting_go_intro': "أود أن أقدم لك تقنية الترك لديفيد آر هوكينز. تساعدك هذه التقنية على التخلص من المشاعر السلبية من خلال الاعتراف بها وقبولها، بدلاً من قمعها أو التعبير عنها.",
        'letting_go_step1': "الخطوة 1: حدد المشاعر التي تشعر بها الآن. هل يمكنك تسميتها؟",
        'letting_go_step2': "الخطوة 2: اسمح لنفسك بالشعور الكامل بهذه العاطفة دون حكم. أين تشعر بها في جسمك؟",
        'letting_go_step3': "الخطوة 3: اسأل نفسك إذا كنت على استعداد للتخلي عن هذا الشعور، حتى لو قليلاً.",
        'letting_go_step4': "الخطوة 4: اسأل نفسك متى يمكنك التخلي عنه. هل يمكنك التخلي عنه الآن؟",
        'letting_go_prompt': "هل ترغب في تجربة تقنية الترك مع ما تشعر به الآن؟",
        'letting_go_yes': "نعم، أود أن أجرب",
        'letting_go_no': "ليس الآن",
    }