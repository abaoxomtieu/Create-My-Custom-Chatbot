from typing import Optional
from pydantic import BaseModel, Field


class CustomChatbotBody(BaseModel):
    conversation_id: str = Field(..., title="id of conversation")
    query: str = Field(..., title="message")
    model_name: Optional[str] = Field(None, title="Model name to use")


class RagAgentBody(BaseModel):
    query: dict = Field(..., title="User's query message in role-based format")
    bot_id: Optional[str] = Field(None, title="Bot ID")
    conversation_id: Optional[str] = Field(None, title="Conversation ID")
    model_name: Optional[str] = Field(None, title="Model name to use")
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hình này là ở đâu vậy?"},
                        {
                            "type": "image",
                            "source_type": "url",
                            "url": "https://example.com/image.jpg",
                        },
                    ],
                },
                "bot_id": "1",
                "prompt": "You are a helpful assistant.",
                "conversation_id": "1",
                "model_name": "gpt-4o"
            }
        }
    }
