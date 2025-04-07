# AMIRA - AI Mental Health Therapeutic Assistant

AMIRA is a comprehensive AI therapist platform designed to interact with human emotions, provide real and effective solutions, and generate detailed reports to assess psychological issues. The platform focuses on three mental health conditions: depression, bipolar disorder, and obsessive-compulsive disorder (OCD).

## Features

- **Emotional Analysis**: Processes and understands human emotions expressed through text conversations
- **Personalized Support**: Provides empathetic and supportive responses tailored to the patient's emotional state and condition
- **Integrated Progress Tracking**: Access progress information directly through Telegram bot buttons
- **Integrated Reporting**: Generate and view therapeutic reports directly in the Telegram interface
- **MongoDB Data Storage**: All patient data, interactions, and reports stored securely in MongoDB
- **Secure Data Handling**: Implements proper error handling and data validation
- **Comprehensive Testing**: Includes unit tests for core components

## Technology Stack

- **Python**: Primary programming language
- **Telegram**: User interface for patient interactions
- **Gemini 2**: AI model for natural language understanding and response generation
- **MongoDB**: Database for storing and managing patient data

## Project Structure

```
amira/
├── bot/                  # Telegram bot implementation
│   ├── __init__.py
│   ├── handlers.py       # Message handlers for the bot with integrated progress and reporting
│   └── bot.py            # Bot initialization and configuration
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── ai_therapist.py   # AI therapist implementation using Gemini 2
│   ├── emotion_analyzer.py # Emotion analysis module
│   └── treatment.py      # Placeholder (treatment recommendations removed)
├── data/                 # Data management
│   ├── __init__.py
│   ├── database.py       # MongoDB connection and operations
│   └── models.py         # Data models for patients and sessions
├── reporting/            # Reporting functionality (integrated with Telegram bot)
│   ├── __init__.py
│   ├── report_generator.py # Generates detailed reports for Telegram interface
│   └── visualizations.py # Creates visualizations for Telegram interface
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_ai_therapist.py    # Tests for AI therapist
│   ├── test_emotion_analyzer.py # Tests for emotion analyzer
│   └── test_database.py  # Tests for database operations
├── config.py             # Configuration settings
├── main.py               # Main application entry point
└── requirements.txt      # Project dependencies
```

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (copy `.env.example` to `.env` and edit):
   - `TELEGRAM_TOKEN`: Your Telegram bot token
   - `GEMINI_API_KEY`: Your Gemini 2 API key
   - `MONGODB_URI`: Your MongoDB connection string
   - `MONGODB_DB_NAME`: Name of your MongoDB database
4. Run the application: `python main.py`
5. Run tests: `python -m unittest discover tests`

## Security Considerations

- **API Keys**: Never commit your API keys to the repository. Use environment variables.
- **Patient Data**: All patient data is stored securely in MongoDB and in the file system.
- **Error Handling**: The system includes comprehensive error handling to prevent data loss.
- **Input Validation**: User inputs are validated to prevent injection attacks.
- **Regular Backups**: Implement regular backups of the MongoDB database and patient data directory.

## Usage

Patients interact with the AI therapist through a Telegram bot. The system analyzes their messages, provides appropriate responses, and tracks their progress over time. Therapists and administrators can access patient dashboards to monitor treatment progress and generate reports.

## License

This project is licensed under the MIT License - see the LICENSE file for details.