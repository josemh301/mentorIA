# Discord Bot con RAG - Inversiones Inmobiliarias

## Overview
Discord bot written in Python that provides real estate investment advice using EdenAI's RAG (Retrieval-Augmented Generation) service. The bot responds to user queries in Spanish and provides detailed investment guidance.

## Recent Changes
- **2025-09-12**: Initial project import from GitHub
- Installed Python 3.11 and all required dependencies (discord.py, requests, python-dotenv)
- Fixed type annotation issue in rag.py for better type safety
- Set up workflow to run Discord bot automatically
- Bot successfully connects to Discord as "MentorIA#6205"
- Fixed EdenAI RAG API integration - confirmed using user's real estate mentorship documents
- Added support for @mentions in channels alongside ! commands
- Implemented retry logic for temporary 404 errors from EdenAI API
- Fixed duplicate response issue with message ID tracking system
- Implemented smart text chunking to fix Discord 50035 error (2000 character limit exceeded)
- Added safe message sending functions that split at natural boundaries (sentences/paragraphs)

## User Preferences
- Spanish language interface (bot commands and responses in Spanish)
- Real estate investment focus
- Console-based logging for bot monitoring

## Project Architecture
### Structure
```
- src/
  - bot.py          # Main Discord bot logic with commands
  - rag.py          # EdenAI RAG API integration
- requirements.txt  # Python dependencies
- README.md        # Project documentation (Spanish)
```

### Key Components
1. **Discord Bot (src/bot.py)**
   - Uses discord.py library v2.6.3
   - Commands: !ping, !ask, !ayuda
   - Handles message chunking for Discord's 2000 character limit
   - Integrated with RAG system for AI responses

2. **RAG Integration (src/rag.py)**
   - Connects to EdenAI's RAG API
   - Uses OpenAI GPT-4o model
   - Configured for real estate investment domain
   - Temperature: 0.1 for consistent responses

### Environment Variables
- DISCORD_BOT_TOKEN: Bot authentication token
- EDENAI_API_KEY: EdenAI service API key
- RAG_PROJECT_ID: Specific RAG project identifier

### Workflow Configuration
- Single workflow: "Discord Bot" 
- Command: `python src/bot.py`
- Output: Console logging
- Status: Running successfully

## Current Status
✅ Bot connects to Discord successfully
✅ All dependencies installed
✅ Environment variables configured
⚠️ RAG API integration may need project-specific configuration