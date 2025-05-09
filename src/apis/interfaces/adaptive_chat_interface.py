from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    content: str = Field(..., title="Message content")
    type: str = Field(..., title="Message type (human/ai)")


class AdaptiveChatBody(BaseModel):
    query: str = Field(..., title="User's query message")
    session_id: Optional[str] = Field(None, title="Session ID for tracking conversation")
    history: Optional[List[ChatMessage]] = Field(None, title="Chat history")
    current_system_prompt: Optional[str] = Field(None, title="Current system prompt being used")
    user_profile: Optional[Dict[str, Any]] = Field(None, title="User profile information if available")
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Tôi muốn tìm hiểu về machine learning",
                "session_id": "abc123",
                "history": [
                    {"content": "Xin chào", "type": "human"},
                    {
                        "content": "Xin chào! Tôi có thể giúp gì cho bạn?",
                        "type": "ai",
                    },
                ],
                "current_system_prompt": "Bạn là trợ lý AI hữu ích, trả lời câu hỏi người dùng một cách chính xác và đầy đủ.",
                "user_profile": {
                    "technical_level": "beginner",
                    "preferred_style": "friendly",
                    "interests": ["AI", "programming"]
                }
            }
        }
    }


class AdaptiveChatResponse(BaseModel):
    bot_message: str = Field(..., title="Bot's response message")
    updated_system_prompt: Optional[str] = Field(None, title="Updated system prompt")
    session_id: str = Field(..., title="Session ID for tracking conversation")
    probing_questions: Optional[List[str]] = Field(None, title="Questions to probe user for more information")
    user_profile_updates: Optional[Dict[str, Any]] = Field(None, title="Updates to the user profile") 