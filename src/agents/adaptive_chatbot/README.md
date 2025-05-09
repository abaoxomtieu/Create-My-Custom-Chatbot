# Adaptive Chatbot System

## Overview

The Adaptive Chatbot is an advanced AI assistant that dynamically adapts its approach to user interactions. It works by analyzing user requests, updating its system prompt, and creating/maintaining user profiles to deliver more personalized and effective responses over time.

## Key Features

1. **Dynamic System Prompt Adjustment**: The chatbot automatically adjusts its system prompt based on the user's requests, knowledge level, and preferred communication style.

2. **User Profiling**: The system builds and maintains profiles for users, tracking their technical knowledge, interests, and communication preferences.

3. **Probing Questions**: When the system needs more information about the user to provide better assistance, it can ask targeted probing questions.

4. **Personalized Responses**: As the system learns about the user, responses become more tailored to their level of understanding and style preferences.

## Flow Diagram

The system uses a LangGraph-based workflow with the following steps:

```
START --> initialize_state --> analyze_user_request --> [conditional branch] 
  --> generate_probing_questions / update_user_profile / generate_bot_response
  --> update_system_prompt --> generate_bot_response --> process_return_value --> trim_history --> END
```

## Components

1. **State Management**: TypedDict classes for handling state throughout the processing pipeline.

2. **Prompt Templates**: Templates for analyzing requests, generating questions, updating system prompts, and creating user profiles.

3. **Core Functions**:
   - `analyze_user_request`: Analyzes the user's message to determine intent and needs
   - `generate_probing_questions`: Creates questions to learn more about the user
   - `update_user_profile`: Maintains the user profile information
   - `update_system_prompt`: Dynamically adjusts the system prompt
   - `generate_bot_response`: Produces the final response using the customized system prompt

4. **API Endpoints**:
   - `/adaptive-chat/chat`: Standard response endpoint
   - `/adaptive-chat/chat/stream`: Streaming response endpoint

## Sample Use Cases

1. **Technical Level Adaptation**: When a user asks a technical question, the system can adjust to provide either basic or in-depth explanations based on their assessed technical level.

2. **Communication Style Matching**: The system can match a user's communication style (formal, casual, concise, etc.) based on their interactions.

3. **Interest-Based Customization**: As the system learns about a user's interests, it can tailor examples and analogies to topics they care about.

## Testing

The system includes comprehensive tests for both the full flow and individual components. Run these tests using:

```
python src/test_adaptive_chatbot.py
```

## API Usage Example

```python
import requests

# Standard request
response = requests.post(
    "http://localhost:8000/adaptive-chat/chat",
    json={
        "query": "Tôi muốn tìm hiểu về machine learning",
        "session_id": "user123",
        "history": [],
        "current_system_prompt": None,
        "user_profile": None
    }
)

# Handle probing questions if needed
if response.json().get("probing_questions"):
    # Display questions to user and get answers
    # Then send a follow-up request with those answers
    pass
else:
    # Display the bot's response
    print(response.json()["bot_message"])
``` 