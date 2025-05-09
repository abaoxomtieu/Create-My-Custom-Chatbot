import json
import uuid
from typing import Dict, List, Any, Optional, Tuple

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.utils.logger import logger
from .data import State, UserProfile, convert_to_langchain_messages
from .prompt import (
    DEFAULT_SYSTEM_PROMPT,
    ANALYZE_REQUEST_TEMPLATE,
    GENERATE_PROBING_QUESTIONS_TEMPLATE,
    UPDATE_SYSTEM_PROMPT_TEMPLATE,
    RESPONSE_TEMPLATE,
    CREATE_USER_PROFILE_TEMPLATE,
)


# Initialize LLM - use whatever is available in your environment
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
        verbose=True,
    )
except Exception:
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            verbose=True,
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise


def initialize_state(state: State) -> State:
    """
    Initialize the state with default values if they are not present.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with default values
    """
    if "session_id" not in state or not state["session_id"]:
        state["session_id"] = str(uuid.uuid4())
    
    if "messages_history" not in state or not state["messages_history"]:
        state["messages_history"] = []
    
    if "current_system_prompt" not in state or not state["current_system_prompt"]:
        state["current_system_prompt"] = DEFAULT_SYSTEM_PROMPT
    
    if "user_profile" not in state or not state["user_profile"]:
        state["user_profile"] = {}
    
    if "messages" not in state:
        state["messages"] = []
    
    return state


async def analyze_user_request(state: State) -> State:
    """
    Analyze the user's request to determine intent and whether we need to update the prompt.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with analysis results
    """
    try:
        # Prepare message history
        history = convert_to_langchain_messages(state["messages_history"])
        
        # Build the prompt
        prompt = ANALYZE_REQUEST_TEMPLATE
        
        # Call the LLM
        response = await llm.ainvoke(
            prompt.format_messages(
                history=history,
                current_system_prompt=state["current_system_prompt"],
                user_message=state["user_message"],
            )
        )
        
        # Parse the JSON response
        try:
            # Clean up the response content to handle potential formatting issues
            content = response.content.strip()
            # Some models might return the JSON with code formatting markers
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            # Parse the JSON
            analysis_result = json.loads(content)
            state["analysis_result"] = analysis_result
            state["prompt_needs_update"] = analysis_result.get("prompt_needs_update", False)
            state["probing_questions_needed"] = analysis_result.get("probing_questions_needed", False)
            
            logger.info(f"Analysis complete: {analysis_result}")
            
            return state
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis result: {e}")
            logger.error(f"Raw response: {response.content}")
            # Try to extract a JSON object from the response if it exists
            try:
                import re
                json_match = re.search(r'({[\s\S]*})', response.content)
                if json_match:
                    json_str = json_match.group(1)
                    analysis_result = json.loads(json_str)
                    state["analysis_result"] = analysis_result
                    state["prompt_needs_update"] = analysis_result.get("prompt_needs_update", False)
                    state["probing_questions_needed"] = analysis_result.get("probing_questions_needed", False)
                    logger.info(f"Successfully extracted JSON with regex: {analysis_result}")
                    return state
            except Exception:
                # If regex extraction fails, use the default fallback
                pass
                
            # Fallback analysis result
            state["analysis_result"] = {
                "intent": "unknown",
                "keywords": [],
                "prompt_needs_update": True,
                "probing_questions_needed": False,
                "confidence": 0.0,
                "reasoning": "Failed to parse the analysis result"
            }
            return state
            
    except Exception as e:
        logger.error(f"Error in analyze_user_request: {e}")
        state["analysis_result"] = {
            "intent": "unknown",
            "keywords": [],
            "prompt_needs_update": True,
            "probing_questions_needed": False,
            "confidence": 0.0,
            "reasoning": f"Error during analysis: {str(e)}"
        }
        return state


async def generate_probing_questions(state: State) -> State:
    """
    Generate probing questions to better understand the user.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with probing questions
    """
    try:
        # Prepare message history
        history = convert_to_langchain_messages(state["messages_history"])
        
        # Build the prompt
        prompt = GENERATE_PROBING_QUESTIONS_TEMPLATE
        
        # Call the LLM
        response = await llm.ainvoke(
            prompt.format_messages(
                history=history,
                user_message=state["user_message"],
                analysis_result=state["analysis_result"],
            )
        )
        
        # Parse the JSON response
        try:
            questions = json.loads(response.content)
            if isinstance(questions, list):
                state["probing_questions"] = questions
                logger.info(f"Generated probing questions: {questions}")
            else:
                logger.error(f"Invalid format for probing questions: {questions}")
                state["probing_questions"] = ["Bạn có thể chia sẻ thêm về nhu cầu của bạn không?"]
            
            return state
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse probing questions: {e}")
            logger.error(f"Raw response: {response.content}")
            state["probing_questions"] = ["Bạn có thể chia sẻ thêm về nhu cầu của bạn không?"]
            return state
            
    except Exception as e:
        logger.error(f"Error in generate_probing_questions: {e}")
        state["probing_questions"] = ["Bạn có thể chia sẻ thêm về nhu cầu của bạn không?"]
        return state


async def update_user_profile(state: State) -> State:
    """
    Update the user profile based on the current conversation.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with updated user profile
    """
    try:
        # Prepare message history
        history = convert_to_langchain_messages(state["messages_history"])
        
        # Build the prompt
        prompt = CREATE_USER_PROFILE_TEMPLATE
        
        # Prepare probing answers (if any)
        probing_answers = "Không có"  # Default
        
        # Call the LLM
        response = await llm.ainvoke(
            prompt.format_messages(
                history=history,
                current_profile=state["user_profile"],
                user_message=state["user_message"],
                probing_answers=probing_answers,
            )
        )
        
        # Parse the JSON response
        try:
            profile_updates = json.loads(response.content)
            if isinstance(profile_updates, dict):
                # Update the existing profile
                if not state["user_profile"]:
                    state["user_profile"] = {}
                
                state["user_profile"].update(profile_updates)
                logger.info(f"Updated user profile: {profile_updates}")
            else:
                logger.error(f"Invalid format for user profile: {profile_updates}")
            
            return state
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse user profile: {e}")
            logger.error(f"Raw response: {response.content}")
            return state
            
    except Exception as e:
        logger.error(f"Error in update_user_profile: {e}")
        return state


async def update_system_prompt(state: State) -> State:
    """
    Update the system prompt based on the user's request and profile.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with new system prompt
    """
    try:
        # Prepare message history
        history = convert_to_langchain_messages(state["messages_history"])
        
        # Build the prompt
        prompt = UPDATE_SYSTEM_PROMPT_TEMPLATE
        
        # Call the LLM
        response = await llm.ainvoke(
            prompt.format_messages(
                history=history,
                current_system_prompt=state["current_system_prompt"],
                user_message=state["user_message"],
                user_profile=state["user_profile"],
                analysis_result=state["analysis_result"],
            )
        )
        
        # Get the new system prompt
        new_system_prompt = response.content.strip()
        state["updated_system_prompt"] = new_system_prompt
        state["final_system_prompt"] = new_system_prompt  # Also set as final
        
        logger.info(f"Updated system prompt: {new_system_prompt}")
        
        return state
            
    except Exception as e:
        logger.error(f"Error in update_system_prompt: {e}")
        state["updated_system_prompt"] = state["current_system_prompt"]  # Keep current
        state["final_system_prompt"] = state["current_system_prompt"]  # Keep current
        return state


async def generate_bot_response(state: State) -> State:
    """
    Generate the bot's response to the user's message.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with bot's response
    """
    try:
        # Prepare message history
        history = convert_to_langchain_messages(state["messages_history"])
        
        # Determine which system prompt to use
        system_prompt = state.get("final_system_prompt", state["current_system_prompt"])
        
        # Build the prompt
        prompt = RESPONSE_TEMPLATE
        
        # Call the LLM
        response = await llm.ainvoke(
            prompt.format_messages(
                history=history,
                system_prompt=system_prompt,
                user_message=state["user_message"],
            )
        )
        
        # Get the bot's response
        bot_message = response.content
        state["bot_message"] = bot_message
        
        logger.info(f"Generated bot response: {bot_message[:100]}...")
        
        return state
            
    except Exception as e:
        logger.error(f"Error in generate_bot_response: {e}")
        state["bot_message"] = "Xin lỗi, tôi đang gặp vấn đề kỹ thuật. Vui lòng thử lại sau."
        return state


async def process_return_value(state: State) -> State:
    """
    Process the final state to prepare the return value.
    
    Args:
        state: Current state
        
    Returns:
        Final state with processed return values
    """
    # Update the message history with the new messages
    if "bot_message" in state and state["bot_message"]:
        # Add the user message to history if not present
        user_msg_in_history = False
        if state["messages_history"]:
            last_msg = state["messages_history"][-1]
            # Check if last_msg is a ChatMessage object or a dictionary
            if hasattr(last_msg, 'type'):  # It's a Pydantic model
                user_msg_in_history = (last_msg.type == "human" and last_msg.content == state["user_message"])
            else:  # It's a dictionary
                user_msg_in_history = (last_msg["type"] == "human" and last_msg["content"] == state["user_message"])
        
        if not user_msg_in_history:
            state["messages_history"].append({
                "content": state["user_message"],
                "type": "human"
            })
        
        # Add the bot message to history
        state["messages_history"].append({
            "content": state["bot_message"],
            "type": "ai"
        })
    
    return state


def trim_history(state: State, max_history: int = 20) -> State:
    """
    Trim the message history to avoid it getting too long.
    
    Args:
        state: Current state
        max_history: Maximum number of messages to keep
        
    Returns:
        State with trimmed history
    """
    if len(state["messages_history"]) > max_history:
        # Keep only the last max_history messages
        state["messages_history"] = state["messages_history"][-max_history:]
    
    return state 