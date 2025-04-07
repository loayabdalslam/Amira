"""Localization module for AMIRA

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
        'switch_language': "Change Language",
        'switch_to_english': "Switch to English",
        'switch_to_arabic': "Switch to Arabic",
        
        # Conditions
        'depression': "Depression",
        'bipolar': "Bipolar Disorder",
        'ocd': "OCD",
        'unknown': "Not sure",
        'anxiety': "Anxiety",
        'adjustment_disorder': "Adjustment Disorder",
        'ptsd': "PTSD",
        'general_stress': "General Stress",
        
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
        'session_date': "Session Date",
        'session_duration': "Session Duration",
        'interaction_count': "Number of Interactions",
        'summary': "Session Summary",
        'condition': "Psychological Assessment",
        'no_summary_available': "No summary available for this session.",
        'previous_session_report': "Here's a summary of your previous session:",
        'no_previous_sessions': "You don't have any previous sessions yet.",
        
        # Letting Go Technique
        'letting_go_intro': "I'd like to introduce you to the Letting Go technique by David R. Hawkins. This technique helps you release negative emotions by acknowledging and accepting them, rather than suppressing or expressing them.",
        'letting_go_step1': "Step 1: Identify the emotion you're feeling right now. Can you name it?",
        'letting_go_step2': "Step 2: Allow yourself to fully feel this emotion without judgment. Where do you feel it in your body?",
        'letting_go_step3': "Step 3: Ask yourself if you're willing to let go of this feeling, even just a little bit.",
        'letting_go_step4': "Step 4: Ask yourself when you could let it go. Could you let it go now?",
        'letting_go_prompt': "Would you like to try the Letting Go technique with what you're feeling right now?",
        'letting_go_yes': "Yes, I'd like to try",
        'letting_go_no': "Not right now",
        'letting_go_complete': "Well done! How do you feel now after applying the Letting Go technique?",
        'letting_go_progress': "You've made great progress with the Letting Go technique. Do you notice any change in your feelings?",
        'letting_go_reminder': "Remember that the Letting Go technique is a skill that develops with practice. The more you practice it, the more effective it becomes.",
        
        # Session management
        'session_started': "A new session has started. How can I help you today?",
        'session_resumed': "Session resumed. Where did we leave off?",
        'session_ended': "Session ended. Thank you for your time.",
        'session_timeout': "It seems we haven't been talking for a while. Would you like to end this session or continue?",
        'continue_session': "Continue Session",
        'end_session': "End Session",
        'session_summary': "Session Summary: {summary}",
        'session_duration_text': "Session Duration: {duration} minutes",
        'session_interaction_count': "Number of interactions in this session: {count}",
        
        # Emotional analysis
        'emotion_detected': "It seems you're feeling {emotion}. Is that right?",
        'emotion_intensity': "Emotion intensity: {intensity}/10",
        'emotion_change': "I've noticed a change in your emotions from {old_emotion} to {new_emotion}.",
        'positive_emotion_reinforcement': "It's great that you're feeling {emotion}! How can we maintain this feeling?",
        'negative_emotion_support': "I'm sorry to hear you're feeling {emotion}. Let's work together to address this feeling.",
        
        # Error messages
        'error_processing': "I'm having trouble processing that right now. Could you please try expressing that in a different way?",
        'connection_error': "There seems to be a connection issue. Could you try again?",
        'invalid_input': "Sorry, I didn't understand that. Could you clarify what you mean?",
        'timeout_error': "The request timed out. Could you try again?",
        
        # Psychological assessment
        'mood_tracking': "Mood Tracking",
        'mood_very_low': "Very Low",
        'mood_low': "Low",
        'mood_neutral': "Neutral",
        'mood_good': "Good",
        'mood_very_good': "Very Good",
        'mood_question': "How would you rate your mood today?",
        'mood_improvement': "Your mood seems to have improved since our last session.",
        'mood_decline': "I notice your mood has declined since our last session. Would you like to talk about what's changed?",
        
        # Additional therapeutic techniques
        'deep_breathing_intro': "Let's try a deep breathing exercise. This can help reduce anxiety and stress.",
        'deep_breathing_step1': "Find a comfortable position and close your eyes if you'd like.",
        'deep_breathing_step2': "Breathe in slowly through your nose for a count of 4.",
        'deep_breathing_step3': "Hold your breath for a count of 2.",
        'deep_breathing_step4': "Exhale slowly through your mouth for a count of 6.",
        'deep_breathing_step5': "Repeat this cycle 5 times.",
        'deep_breathing_complete': "How do you feel after the breathing exercise?",
        
        # User engagement
        'check_in': "It's been a few days since our last conversation. How have you been feeling?",
        'daily_reflection': "What's one positive thing that happened today?",
        'weekly_goal': "Would you like to set a small goal for this week?",
        'goal_followup': "How did you do with the goal we set last time?"
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
        'switch_language': "تغيير اللغة",
        'switch_to_english': "Switch to English",
        'switch_to_arabic': "التحويل إلى العربية",
        
        # Conditions
        'depression': "الاكتئاب",
        'bipolar': "الاضطراب ثنائي القطب",
        'ocd': "الوسواس القهري",
        'unknown': "مش متأكد",
        'anxiety': "القلق",
        'adjustment_disorder': "اضطراب التكيف",
        'ptsd': "اضطراب ما بعد الصدمة",
        'general_stress': "الضغط العام",
        
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
        'session_date': "تاريخ الجلسة",
        'session_duration': "مدة الجلسة",
        'interaction_count': "عدد التفاعلات",
        'summary': "ملخص الجلسة",
        'condition': "التقييم النفسي",
        'no_summary_available': "لا يوجد ملخص متاح لهذه الجلسة.",
        'previous_session_report': "إليك ملخص جلستك السابقة:",
        'no_previous_sessions': "ليس لديك أي جلسات سابقة حتى الآن.",
        
        # Session management
        'session_started': "بدأت جلسة جديدة. كيف يمكنني مساعدتك اليوم؟",
        'session_resumed': "تم استئناف الجلسة. أين توقفنا؟",
        'session_ended': "انتهت الجلسة. شكرا لك على وقتك.",
        'session_timeout': "يبدو أننا لم نتحدث لفترة. هل ترغب في إنهاء هذه الجلسة أم الاستمرار؟",
        'continue_session': "استمرار الجلسة",
        'end_session': "إنهاء الجلسة",
        'session_summary': "ملخص الجلسة: {summary}",
        'session_duration_text': "مدة الجلسة: {duration} دقيقة",
        'session_interaction_count': "عدد التفاعلات في هذه الجلسة: {count}",
        
        # Emotional analysis
        'emotion_detected': "يبدو أنك تشعر بـ {emotion}. هل هذا صحيح؟",
        'emotion_intensity': "شدة المشاعر: {intensity}/10",
        'emotion_change': "لقد لاحظت تغييرًا في مشاعرك من {old_emotion} إلى {new_emotion}.",
        'positive_emotion_reinforcement': "من الرائع أن تشعر بـ {emotion}! كيف يمكننا الحفاظ على هذا الشعور؟",
        'negative_emotion_support': "أنا آسفة لسماع أنك تشعر بـ {emotion}. دعنا نعمل معًا للتعامل مع هذا الشعور.",
        
        # Letting Go Technique
        'letting_go_intro': "أود أن أقدم لك تقنية الترك لديفيد آر هوكينز. تساعدك هذه التقنية على التخلص من المشاعر السلبية من خلال الاعتراف بها وقبولها، بدلاً من قمعها أو التعبير عنها.",
        'letting_go_step1': "الخطوة 1: حدد المشاعر التي تشعر بها الآن. هل يمكنك تسميتها؟",
        'letting_go_step2': "الخطوة 2: اسمح لنفسك بالشعور الكامل بهذه العاطفة دون حكم. أين تشعر بها في جسمك؟",
        'letting_go_step3': "الخطوة 3: اسأل نفسك إذا كنت على استعداد للتخلي عن هذا الشعور، حتى لو قليلاً.",
        'letting_go_step4': "الخطوة 4: اسأل نفسك متى يمكنك التخلي عنه. هل يمكنك التخلي عنه الآن؟",
        'letting_go_prompt': "هل ترغب في تجربة تقنية الترك مع ما تشعر به الآن؟",
        'letting_go_yes': "نعم، أود أن أجرب",
        'letting_go_no': "ليس الآن",
        'letting_go_complete': "أحسنت! كيف تشعر الآن بعد تطبيق تقنية الترك؟",
        'letting_go_progress': "لقد أحرزت تقدمًا رائعًا مع تقنية الترك. هل تلاحظ أي تغيير في مشاعرك؟",
        'letting_go_reminder': "تذكر أن تقنية الترك هي مهارة تتطور مع الممارسة. كلما مارستها أكثر، أصبحت أكثر فعالية.",
        
        # Error messages
        'error_processing': "أواجه صعوبة في معالجة ذلك الآن. هل يمكنك محاولة التعبير عن ذلك بطريقة مختلفة؟",
        'connection_error': "يبدو أن هناك مشكلة في الاتصال. هل يمكنك المحاولة مرة أخرى؟",
        'invalid_input': "عذرًا، لم أفهم ذلك. هل يمكنك توضيح ما تعنيه؟",
        'timeout_error': "انتهت مهلة الطلب. هل يمكنك المحاولة مرة أخرى؟",
        
        # Psychological assessment
        'mood_tracking': "تتبع المزاج",
        'mood_very_low': "منخفض جدًا",
        'mood_low': "منخفض",
        'mood_neutral': "محايد",
        'mood_good': "جيد",
        'mood_very_good': "جيد جدًا",
        'mood_question': "كيف تقيم مزاجك اليوم؟",
        'mood_improvement': "يبدو أن مزاجك قد تحسن منذ جلستنا الأخيرة.",
        'mood_decline': "ألاحظ أن مزاجك قد انخفض منذ جلستنا الأخيرة. هل ترغب في التحدث عما تغير؟",
        
        # Additional therapeutic techniques
        'deep_breathing_intro': "دعنا نجرب تمرين التنفس العميق. يمكن أن يساعد هذا في تقليل القلق والتوتر.",
        'deep_breathing_step1': "ابحث عن وضع مريح وأغلق عينيك إذا كنت ترغب في ذلك.",
        'deep_breathing_step2': "تنفس ببطء من خلال أنفك لمدة 4 عدات.",
        'deep_breathing_step3': "احبس أنفاسك لمدة عدتين.",
        'deep_breathing_step4': "ازفر ببطء من خلال فمك لمدة 6 عدات.",
        'deep_breathing_step5': "كرر هذه الدورة 5 مرات.",
        'deep_breathing_complete': "كيف تشعر بعد تمرين التنفس؟",
        
        # User engagement
        'check_in': "لقد مرت بضعة أيام منذ محادثتنا الأخيرة. كيف كان شعورك؟",
        'daily_reflection': "ما هو الشيء الإيجابي الذي حدث اليوم؟",
        'weekly_goal': "هل ترغب في تحديد هدف صغير لهذا الأسبوع؟",
        'goal_followup': "كيف كان أداؤك مع الهدف الذي حددناه في المرة الماضية؟"
    }