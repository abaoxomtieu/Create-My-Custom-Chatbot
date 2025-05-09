from typing import List, Dict, Any, Optional, TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class Message(TypedDict):
    content: str
    type: Literal["human", "ai"]


class UserProfile(TypedDict, total=False):
    """User profile information to personalize interactions."""
    technical_level: Optional[str]  # e.g., "beginner", "intermediate", "expert"
    preferred_style: Optional[str]  # e.g., "friendly", "professional", "concise" 
    interests: Optional[List[str]]  # Topics the user is interested in
    domain_knowledge: Optional[Dict[str, str]]  # Subject areas and knowledge level
    language_preference: Optional[str]  # Preferred language
    personality_traits: Optional[Dict[str, float]]  # e.g., {"openness": 0.8, "friendliness": 0.9}


class State(TypedDict, total=False):
    """State for the adaptive chatbot agent."""
    # Input
    user_message: str  # Current user message
    session_id: str  # Unique identifier for the conversation
    messages_history: List[Message]  # Full conversation history
    
    # Conversation context
    current_system_prompt: Optional[str]  # Current system prompt
    user_profile: Optional[UserProfile]  # User profile information
    
    # Analysis results
    analysis_result: Optional[Dict[str, Any]]  # Results from analyzing user request
    prompt_needs_update: Optional[bool]  # Whether the prompt needs to be updated
    probing_questions_needed: Optional[bool]  # Whether probing questions are needed
    
    # Intermediate results
    probing_questions: Optional[List[str]]  # Questions to ask the user
    updated_system_prompt: Optional[str]  # New system prompt after update
    
    # Final outputs
    final_system_prompt: Optional[str]  # Final system prompt used
    bot_message: Optional[str]  # Bot's response message
    
    # Messages for LangGraph
    messages: List[tuple]  # Messages in LangGraph format
    

def convert_to_langchain_messages(history: List[Message | Any]) -> List[HumanMessage | AIMessage]:
    """
    Convert chat history to LangChain message format.
    
    Args:
        history: List of chat messages with type and content
        
    Returns:
        List of LangChain message objects
    """
    result = []
    for message in history:
        # Check if message is a dictionary or a Pydantic model
        if hasattr(message, 'type') and hasattr(message, 'content'):  # It's a Pydantic model
            msg_type = message.type
            content = message.content
        elif isinstance(message, dict) and 'type' in message and 'content' in message:  # It's a dictionary
            msg_type = message["type"]
            content = message["content"]
        else:
            # Skip invalid message formats
            continue
            
        if msg_type == "human":
            result.append(HumanMessage(content=content))
        else:
            result.append(AIMessage(content=content))
    return result


def create_chat_history(messages: List[HumanMessage | AIMessage | SystemMessage]) -> List[Message]:
    """
    Convert LangChain messages to chat history format.
    
    Args:
        messages: List of LangChain message objects
        
    Returns:
        List of chat messages with type and content
    """
    result = []
    for message in messages:
        if isinstance(message, HumanMessage):
            result.append({"content": message.content, "type": "human"})
        elif isinstance(message, AIMessage):
            result.append({"content": message.content, "type": "ai"})
    return result 