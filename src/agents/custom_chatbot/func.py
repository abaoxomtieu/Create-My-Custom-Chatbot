from typing import TypedDict,Optional
from langchain_core.messages import AnyMessage, ToolMessage
from langgraph.graph.message import add_messages
from typing import Sequence, Annotated
from src.agents.custom_chatbot.prompt import (
    create_system_chain,
    collection_info_agent,
)
from src.utils.logger import logger
import re
from src.config.mongo import bot_crud


class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    remaining_steps: int
    prompt: Optional[str]
    name: Optional[str]


def get_info_collection(messages):
    for idx, message in enumerate(messages):
        if isinstance(message, ToolMessage):
            break
    info = messages[idx - 1].tool_calls[0].get("args", {}).get("info", "")
    name = messages[idx - 1].tool_calls[0].get("args", {}).get("name", "")
    return name, info


async def create_prompt(state: State):
    messages = state.get("messages")
    name, info = get_info_collection(messages)
    logger.info(f"create_prompt {info}")
    res = await create_system_chain.ainvoke({"info": info})
    return {"prompt": res.content, "name": name}


async def save_prompt(state: State):
    prompt = state["prompt"]
    matches = re.findall(r"```(.*?)```", prompt, re.DOTALL)
    if matches:
        prompt = matches[0]
    name = state["name"]
    await bot_crud.create({"name": name, "prompt": prompt, "tools": []})
