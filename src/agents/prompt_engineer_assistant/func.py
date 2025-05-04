from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from .prompt import create_prompt_assistant_chain, prompt_engineer_creator_chain
from .tools import prompt_create_complete
from langchain_core.messages import trim_messages, AnyMessage

from src.utils.helper import convert_message, fake_token_counter
import os


class State(TypedDict):
    user_query: str | AnyMessage
    messages_history: list
    messages: Annotated[Sequence[AnyMessage], add_messages]
    final_response: str


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


async def create_prompt_assistant(state: State):
    response = await create_prompt_assistant_chain.ainvoke(state)
    return {
        "final_response": response.content,
        "messages": response,
    }


async def complete_prompt(state: State):
    tool_message = state["messages"][-1]
    if (
        hasattr(tool_message, "tool_calls")
        and tool_message.tool_calls
        and tool_message.tool_calls[0]["name"] == prompt_create_complete.name
    ):
        try:
            tool_call = tool_message.tool_calls[0]
            role = str(tool_call["args"]["role"])
            context = str(tool_call["args"]["context"])
            input_values = str(tool_call["args"]["input_values"])
            instructions = str(tool_call["args"]["instructions"])
            guidelines = str(tool_call["args"]["guidelines"])
            output_format = str(tool_call["args"]["output_format"])
            response = await prompt_engineer_creator_chain.ainvoke(
                {
                    "role": role,
                    "context": context,
                    "input_values": input_values,
                    "instructions": instructions,
                    "guidelines": guidelines,
                    "output_format": output_format,
                }
            )
            return {
                "final_response": response.content,
                "messages": response,
            }
        except Exception as e:
            return {
                "final_response": str(e),
                "messages": tool_message,
            }
