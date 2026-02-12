# EHR Documentation Assistant

An AI-powered system for medical consultation transcription, SOAP note generation, examination recommendations, and drug safety checking.

## Overview

This system automates the documentation workflow for medical consultations by:
1. Transcribing real-time speech to text
2. Generating structured SOAP notes from consultation transcripts
3. Recommending diagnostic examinations based on clinical context
4. Checking for drug interactions, allergies, and contraindications and give recommendations accordingly

## Architecture


- **`ehr_agent.py`**: Main class for CLI interface
- **`app.py`**: Flask backend for web interface
- **`speech_to_text.py`**: Speech Recognition module
- **`soap_generator.py`**: LLM-based SOAP note generation (Gemini)
- **`examination_recommender.py`**: AI-powered test recommendations
- **`drug_checker.py`**: Drug safety validation using LLM analysis

## Tech Stack

- **LLM**: Google Gemini 2.5 Flash/Pro
- **Speech Recognition**: Google Speech Recognition API
- **Backend**: Flask (web), Python CLI with Rich
- **Frontend**: React
- **Audio**: PyAudio for microphone input

## Setup

### Prerequisites

- Python 3.8+
- Google API key with Gemini API access
- Microphone access (for speech input)

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
GOOGLE_API_KEY=api_key
GEMINI_MODEL=gemini-2.5-flash  
```

## Usage

### Web Interface

```bash
python run_web.py
```
Access at `http://localhost:5000`

### CLI Interface

```bash
python ehr_agent.py
```

Follow the interactive prompts to:
1. Enter patient information
2. Record/transcribe consultation
3. Generate SOAP notes
4. Get examination recommendations
5. Check drug conflicts

## Future Improvements

- Add persistent storage for patient history
- Add structured logging and observability
- Support streaming responses for better UX
- Implement caching for repeated queries

## Project Structure

```
.
├── ehr_agent.py              # CLI main entry point
├── app.py                    # Flask web server
├── soap_generator.py         # SOAP note generation
├── examination_recommender.py # Test recommendations
├── drug_checker.py           # Drug safety checks
├── speech_to_text.py         # Speech transcription
├── voice_recorder.py         # Audio recording
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── templates/                # HTML templates
├── static/                   # CSS/JS assets
└── output/                   # Generated reports
```



## Authors

Yuran Zhang - Yuranz6
Rubing Zhang - baisiyou 