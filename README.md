# Multilingual Campus Chatbot MVP

A language-agnostic chatbot designed for campus offices to handle routine queries in multiple regional languages.

## Features

- **Multilingual Support**: Hindi, English, Gujarati, Marathi, Rajasthani
- **Intent Recognition**: Basic keyword matching for common campus queries
- **Context Management**: Session-based conversation memory
- **FAQ Knowledge Base**: Pre-loaded campus information
- **Conversation Logging**: Daily logs for continuous improvement
- **Web Integration**: Embeddable chat widget
- **Human Handoff**: Fallback to human contact when needed

## Project Structure

```
multilingual-campus-chatbot/
├── backend/           # FastAPI backend
├── frontend/          # Web interface
├── data/             # Knowledge base and conversation logs
├── docs/             # Documentation
├── docker-compose.yml # Container orchestration
└── README.md         # This file
```

## Quick Start

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Start backend: `cd backend && python main.py`
3. Open `frontend/index.html` in browser
4. Start chatting in your preferred language!

## Supported Languages

- English
- Hindi (हिंदी)
- Gujarati (ગુજરાતી)
- Marathi (मराठी)
- Rajasthani (राजस्थानी)

## Target Queries

- Fee deadlines and payment procedures
- Scholarship information and forms
- Timetable changes and schedules
- Admission procedures
- Exam schedules and results
- Campus facilities and services

## Deployment

The chatbot can be deployed on college websites and integrated with popular messaging platforms for maximum reach.

## Maintenance

Designed to be maintained by student volunteers with comprehensive documentation and logging features.
