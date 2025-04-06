# AMIRA - AI Mental Health Therapeutic Assistant

AMIRA is a comprehensive AI therapist platform designed to interact with human emotions, provide real and effective solutions, and generate detailed reports to assess psychological issues. The platform focuses on three mental health conditions: depression, bipolar disorder, and obsessive-compulsive disorder (OCD).

## Features

- **Emotional Analysis**: Processes and understands human emotions expressed through text conversations
- **Personalized Solutions**: Provides practical, evidence-based solutions tailored to the patient's emotional state and condition
- **Detailed Reporting**: Generates comprehensive reports to evaluate the severity of psychological conditions and track progress
- **Patient Dashboard**: Visualizes treatment journey with metrics like mood trends and engagement frequency
- **Patient Record System**: Maintains comprehensive records for each patient in dedicated folders
- **MongoDB Integration**: Tracks patient interactions, emotional states, and treatment progress

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
│   ├── handlers.py       # Message handlers for the bot
│   └── bot.py            # Bot initialization and configuration
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── ai_therapist.py   # AI therapist implementation using Gemini 2
│   ├── emotion_analyzer.py # Emotion analysis module
│   └── treatment.py      # Treatment recommendation system
├── data/                 # Data management
│   ├── __init__.py
│   ├── database.py       # MongoDB connection and operations
│   └── models.py         # Data models for patients and sessions
├── reporting/            # Reporting functionality
│   ├── __init__.py
│   ├── report_generator.py # Generates detailed reports
│   └── visualizations.py # Creates visualizations for dashboards
├── dashboard/            # Dashboard implementation
│   ├── __init__.py
│   └── dashboard.py      # Patient dashboard generation
├── utils/                # Utility functions
│   ├── __init__.py
│   └── helpers.py        # Helper functions
├── config.py             # Configuration settings
├── main.py               # Main application entry point
└── requirements.txt      # Project dependencies
```

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `TELEGRAM_TOKEN`: Your Telegram bot token
   - `GEMINI_API_KEY`: Your Gemini 2 API key
   - `MONGODB_URI`: Your MongoDB connection string
4. Run the application: `python main.py`

## Usage

Patients interact with the AI therapist through a Telegram bot. The system analyzes their messages, provides appropriate responses, and tracks their progress over time. Therapists and administrators can access patient dashboards to monitor treatment progress and generate reports.

## License

This project is licensed under the MIT License - see the LICENSE file for details.