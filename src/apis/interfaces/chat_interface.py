from typing import Optional
from pydantic import BaseModel, Field


class ChatBody(BaseModel):
    query: str = Field(..., title="User's query messages")
    history: Optional[list] = Field(None, title="Chat history")
    lesson_name: Optional[str] = Field(None, title="Lesson name")
    subject_name: Optional[str] = Field(None, title="Subject name")
    class_number: Optional[int] = Field(None, title="Class number")
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Hệ thống có những tính năng gì",
                "history": [
                    {"content": "Bạn là ai vậy", "type": "human"},
                    {
                        "content": "Tôi là AI hỗ trợ cho hệ thống LearnMigo",
                        "type": "ai",
                    },
                ],
                "language": "Vietnamese",
                "topic": "education",
            }
        }
    }


class PrimaryChatBody(ChatBody):
    pass


class TutorChatBody(ChatBody):
    filter: Optional[dict] = Field(None, title="Filter")
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Vai trò của tri thức lịch sử là gì",
                "history": [
                    {"content": "Môn này là gì", "type": "human"},
                    {
                        "content": "Lịch sử về Châu Á",
                        "type": "ai",
                    },
                ],
                "language": "Vietnamese",
                "topic": "education",
                "filter": {"lesson_id": "L01"},
            }
        }
    }


class HighlightExplainBody(BaseModel):
    domain: str = Field(..., title="Domain")
    question: str = Field(..., title="User's query messages")
    highlight_terms: str = Field(..., title="Highlight terms")
    before_highlight_paragraph: str = Field(..., title="Before highlight paragraph")
    after_highlight_paragraph: str = Field(..., title="After highlight paragraph")
    language: str = Field("Vietnamese", title="Language")
    model_config = {
        "json_schema_extra": {
            "example": {
                "language": "Vietnamese",
                "domain": "Machine Learning",
                "question": "What does overfitting mean and why is it a problem?",
                "highlight_terms": "overfitting",
                "before_highlight_paragraph": "Overfitting happens when a machine learning model performs well on the training data but poorly on unseen data. This is because the model has learned not just the underlying patterns but also the noise in the training dataset. In contrast, a well-generalized model captures patterns that apply to new data as well.",
                "after_highlight_paragraph": "Overfitting happens when a machine learning model performs well on the training data but poorly on unseen data. This is because the model has learned not just the underlying patterns but also the noise in the training dataset. In contrast, a well-generalized model captures patterns that apply to new data as well.",
            }
        }
    }

class CustomChatbotBody(BaseModel):
    conversation_id: str = Field(...,title='id of conversation')
    query: str = Field(...,title='message')