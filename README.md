# Custom-AI

Advanced AI Services including Adaptive Chatbot capabilities.

## Features

### Adaptive Chatbot

The Adaptive Chatbot dynamically adapts to user interactions by analyzing requests, customizing system prompts, and building user profiles for personalized responses.

Key capabilities:
- Dynamic system prompt adjustment based on user needs
- User profiling to track knowledge level and preferences
- Probing questions when more information is needed
- Personalized responses based on interaction history

See the [Adaptive Chatbot Documentation](src/agents/adaptive_chatbot/README.md) for more details.

## Installation

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Run the FastAPI application with hot-reloading
python app.py
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, access the Swagger documentation at:
http://localhost:8000/

## Development

### Project Structure

```
├── app.py                  # Main application entry point
├── requirements.txt        # Project dependencies
├── src/                    # Source code
│   ├── agents/             # AI agents
│   │   ├── adaptive_chatbot/  # Adaptive chatbot implementation
│   │   ├── primary_chatbot/   # Primary chatbot implementation
│   │   └── ...
│   ├── apis/               # API endpoints
│   │   ├── interfaces/     # Request/response models
│   │   └── routers/        # API routers
│   ├── config/             # Configuration
│   └── utils/              # Utility functions
```

### Testing

```bash
# Run adaptive chatbot tests
python src/test_adaptive_chatbot.py

# Run primary chatbot tests
python src/test_primary_chatbot.py
```
