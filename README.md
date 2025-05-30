# AI Service Backend

## Overview
AI Service is a powerful backend service that enables the creation and management of custom AI chatbots. The service provides two main functionalities:

1. **Custom Chatbot Creation**
   - Interactive prompt generation for new chatbots
   - Intelligent information collection from users
   - Automatic prompt refinement and optimization
   - MongoDB storage for chatbot configurations

2. **Template-based Chatbot Processing**
   - RAG (Retrieval-Augmented Generation) based responses
   - Document processing and indexing
   - Streaming response support
   - Multiple model support (GPT-4, Gemini, etc.)

## Architecture

### Core Components

1. **Custom Chatbot Module**
   - `custom_chatbot/flow.py`: Main workflow for chatbot creation
   - `custom_chatbot/prompt.py`: Prompt templates and system messages
   - `custom_chatbot/func.py`: Core functions for prompt generation and storage

2. **RAG Agent Module**
   - `rag_agent_template/flow.py`: RAG-based response generation
   - Document processing and vector storage
   - Streaming response handling

3. **API Endpoints**
   - `/ai/custom_chatbot/stream`: Create and stream custom chatbot responses
   - `/ai/rag_agent_template/stream`: Stream RAG-based responses
   - `/ai/chatbots`: CRUD operations for chatbot management
   - `/ai/ingress`: Document processing and indexing

### Database Schema

```json
{
  "chatbot": {
    "id": "string",
    "name": "string",
    "prompt": "string",
    "tools": ["string"],
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

## API Documentation

### Custom Chatbot Creation

```http
POST /ai/custom_chatbot/stream
Content-Type: application/json

{
  "conversation_id": "string",
  "query": "string",
  "model_name": "string"
}
```

### RAG Agent Template

```http
POST /ai/rag_agent_template/stream
Content-Type: application/json

{
  "bot_id": "string",
  "query": "string",
  "conversation_id": "string",
  "model_name": "string"
}
```

### Chatbot Management

```http
GET /ai/chatbots
GET /ai/chatbots/{chatbot_id}
PUT /ai/chatbots/{chatbot_id}
```

## Setup and Installation

1. **Prerequisites**
   - Python 3.8+
   - MongoDB
   - Required Python packages (see requirements.txt)

2. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```env
   MONGODB_URI=your_mongodb_uri
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Running the Service**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 7860 --reload
   ```

## Features

### Custom Chatbot Creation
- Interactive prompt generation
- Intelligent information collection
- Automatic prompt refinement
- MongoDB storage integration

### RAG-based Processing
- Document processing and indexing
- Vector storage for efficient retrieval
- Streaming response support
- Multiple model support

### Document Processing
- File upload and processing
- Chunking and indexing
- Vector storage integration
- Automatic tool addition

## Development

### Project Structure
```
BE/
├── src/
│   ├── agents/
│   │   ├── custom_chatbot/
│   │   └── rag_agent_template/
│   ├── apis/
│   │   ├── interfaces/
│   │   └── routers/
│   ├── config/
│   └── utils/
├── test/
├── app.py
└── requirements.txt
```

### Adding New Features
1. Create new router in `src/apis/routers/`
2. Define interfaces in `src/apis/interfaces/`
3. Implement business logic in `src/agents/`
4. Add tests in `test/`

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
