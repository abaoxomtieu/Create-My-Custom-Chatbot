from math import log
import os
from typing import TypedDict, Optional, List, Literal
from langchain_core.documents import Document
from langchain_core.tools import tool
from src.utils.helper import (
    fake_token_counter,
    convert_list_context_source_to_str,
    convert_message,
)
from src.utils.logger import logger
from langchain_core.messages import trim_messages, AnyMessage
from .prompt import entry_chain, build_lesson_plan_chain
from .data import primary_level_format, high_school_level_format
from typing import Annotated, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage


class State(TypedDict):
    user_query: str | AnyMessage
    messages_history: list
    document_id_selected: Optional[List]
    lesson_name: str
    subject_name: str
    class_number: int
    entry_response: str
    build_lesson_plan_response: list[AnyMessage]
    final_response: str
    messages: Annotated[Sequence[AnyMessage], add_messages]


def trim_history(state: State):
    history = (
        convert_message(state["messages_history"])
        if state.get("messages_history")
        else None
    )

    if not history:
        return {"messages_history": []}

    chat_message_history = trim_messages(
        history,
        strategy="last",
        token_counter=fake_token_counter,
        max_tokens=int(os.getenv("HISTORY_TOKEN_LIMIT", 4000)),
        start_on="human",
        end_on="ai",
        include_system=False,
        allow_partial=False,
    )
    return {"messages_history": chat_message_history}


async def entry(state: State):
    logger.info(f"Entry {state['messages']}")
    entry_response: AnyMessage = await entry_chain.ainvoke(
        {"messages": state["messages"]}
    )
    logger.info(f"Entry response: {entry_response}")
    logger.info(f"Entry response tool_calls: {entry_response.content}")
    # Check if entry_response has tool_calls attribute and it's not empty
    if (
        hasattr(entry_response, "tool_calls")
        and entry_response.tool_calls
        and len(entry_response.tool_calls) > 0
        and any(
            tool_call["name"] == "EntryExtractor"
            for tool_call in entry_response.tool_calls
        )
        and "args" in entry_response.tool_calls[0]
        and "class_number" in entry_response.tool_calls[0]["args"]
        and "subject_name" in entry_response.tool_calls[0]["args"]
        and "lesson_name" in entry_response.tool_calls[0]["args"]
    ):
        logger.info("Vô đây")
        class_number = str(int(entry_response.tool_calls[0]["args"]["class_number"]))
        subject_name = str(entry_response.tool_calls[0]["args"]["subject_name"])
        lesson_name = str(entry_response.tool_calls[0]["args"]["lesson_name"])
        return {
            "entry_response": entry_response.content,
            "class_number": class_number,
            "subject_name": subject_name,
            "lesson_name": lesson_name,
        }
    logger.info("không vô")
    return {
        "entry_response": entry_response.content,
        "class_number": None,
        "subject_name": None,
        "lesson_name": None,
        "final_response": entry_response.content,
    }


async def build_lesson_plan(state: State):
    logger.info(f"build_lesson_plan {state['messages']}")
    has_change_lesson = any(
        hasattr(message, "tool_calls")
        and any(tool_call["name"] == "ChangeLesson" for tool_call in message.tool_calls)
        for message in state["messages"]
    )
    has_extract_lesson = any(
        hasattr(message, "tool_calls")
        and any(
            tool_call["name"] == "extract_lesson_content"
            for tool_call in message.tool_calls
        )
        for message in state["messages"]
    )
    if has_change_lesson and not has_extract_lesson:
        state["messages"] = []
        state["messages_history"] = []
    if has_extract_lesson and has_change_lesson:
        state["messages"] = [
            message
            for message in state["messages"]
            if not hasattr(message, "tool_calls")
            or not any(
                tool_call["name"] == "ChangeLesson" for tool_call in message.tool_calls
            )
        ]
    class_number = state["class_number"]
    if int(class_number) > 5:
        lesson_plan_format = high_school_level_format
    else:
        lesson_plan_format = primary_level_format
    state["lesson_plan_format"] = lesson_plan_format
    build_lesson_plan_response = await build_lesson_plan_chain.ainvoke(state)

    return {
        "build_lesson_plan_response": [build_lesson_plan_response],
        "messages": build_lesson_plan_response,
        "final_response": build_lesson_plan_response.content,
    }


def change_lesson(state: State):
    build_lesson_plan_response = state["build_lesson_plan_response"][-1]
    logger.info(f"Build lesson plan response: {build_lesson_plan_response}")

    # Check if there are tool calls in the response
    if (
        hasattr(build_lesson_plan_response, "tool_calls")
        and build_lesson_plan_response.tool_calls
    ):
        # Extract values from tool_calls
        try:
            # Get the first tool call (should be ChangeLesson)
            tool_call = build_lesson_plan_response.tool_calls[0]

            # Extract class_number (handle float conversion if needed)
            class_number_value = tool_call["args"]["class_number"]
            if isinstance(class_number_value, float):
                class_number = str(int(class_number_value))
            else:
                class_number = str(class_number_value)

            # Extract subject and lesson name
            subject_name = str(tool_call["args"]["subject_name"])
            lesson_name = str(tool_call["args"]["lesson_name"])

            logger.info(
                f"Extracted lesson data: class={class_number}, subject={subject_name}, lesson={lesson_name}"
            )

            return {
                "class_number": class_number,
                "subject_name": subject_name,
                "lesson_name": lesson_name,
            }
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extracting lesson data: {e}")

    # Default values if extraction fails
    logger.warning("Could not extract lesson data from response")
    return {
        "class_number": None,
        "subject_name": None,
        "lesson_name": None,
    }
