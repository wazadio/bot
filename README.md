# KK Bot

A scalable Telegram bot built with Python that uses a worker-based architecture for handling business logic.

## 🏗️ Architecture Overview

This bot uses a **separation of concerns** architecture with three main layers:

### 1. **Handlers Layer** (`src/handlers/`)
The **interface layer** between Telegram's API and your business logic. Handlers are responsible for:

- **Receiving updates** from Telegram (messages, commands, button presses)
- **Providing immediate user feedback** and user experience
- **Routing requests** to appropriate services
- **Managing conversation flows** and user interactions


### 2. **Workers Layer** (`src/workers/`)
The **scheduler setup layer** 


### 3. **Services Layer** (`src/services/`)
The **business logic layer** 
External integrations and utilities (database, APIs, etc.)

### 3. **Services Layer** (`src/repository/`)
The **query layer** 
All query done here

## 🔄 How Handlers Work

```
User sends message → Telegram → Handler → Service → Repository → Response → User
                                    ↓
                               Queue for async processing
```

### Example Flow:

1. **User types**: "I want to register"
2. **Message Handler**: Recognizes registration intent
3. **Handler**: Starts conversation flow, asks for name
4. **User responds**: "John Doe"
5. **Handler**: Asks for email, updates session state
6. **Service**: Validates and processes registration
7. **Repository**: Query into database and convert it to model
8. **Handler**: Confirms success to user

## Project Structure

```
kk_telegram_bot/
├── src/
│   ├── workers/                 # Scheduler set up
│   ├── handlers/                # Telegram message handlers
│   ├── services/                # Business logic
│   ├── models/                  # Data models
│   └── utils/                   # Utility functions
├── config/
│   └── settings.py              # Configuration settings
├── tests/                       # Test files
├── logs/                        # Log files
├── venv/                        # Virtual environment
├── main.py                      # Main application entry point
└── requirements.txt             # Python dependencies
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure env in `.env`:
- Add your Telegram bot token
- Configure database and Redis settings
- Adjust worker configurations

4. Run the bot:
```bash
python main.py
```

**Or simply using docker**
Run
```bash
docker.sh
```

## Testing

Run tests with:
```bash
python -m pytest tests/
```

## Contributing

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation
4. Follow Python best practices and PEP 8
