from typing import TypedDict, Optional, List
from langchain_core.messages import AnyMessage, ToolMessage
from langgraph.graph.message import add_messages
from .prompt import rag_answering_chain_tool, rag_answering_chain
from typing import Sequence, Annotated
from langchain_core.messages import RemoveMessage
from langchain_core.documents import Document
from .tools import retrieve_document
from src.utils.helper import convert_list_context_source_to_str
from src.utils.logger import logger

tools = [retrieve_document]


class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    selected_ids: Optional[List[str]]
    selected_documents: Optional[List[Document]]
    tools: list
    prompt: str


def trim_history(state: State):
    history = state.get("messages", [])
    if len(history) > 10:
        num_to_remove = len(history) - 10
        remove_messages = [
            RemoveMessage(id=history[i].id) for i in range(num_to_remove)
        ]
        return {
            "messages": remove_messages,
            "selected_ids": [],
            "selected_documents": [],
        }

    return {}


def execute_tool(state: State):
    tool_calls = state["messages"][-1].tool_calls
    tool_name_to_func = {tool.name: tool for tool in tools}
    selected_ids = []
    selected_documents = []
    tool_messages = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        tool_func = tool_name_to_func.get(tool_name)
        if tool_func:
            if tool_name == "retrieve_document":
                documents = tool_func.invoke(tool_args.get("query"))
                documents = dict(documents)
                context_str = documents.get("context_str", "")
                selected_documents = documents.get("selected_documents", [])
                selected_ids = documents.get("selected_ids", [])
                if documents:
                    tool_messages.append(
                        ToolMessage(
                            tool_call_id=tool_id,
                            content=context_str,
                        )
                    )
                continue
            tool_response = tool_func.invoke(tool_args)
            tool_messages.append(tool_response)

    return {
        "selected_ids": selected_ids,
        "selected_documents": selected_documents,
        "messages": tool_messages,
    }


def generate_answer_rag(state: State):
    messages = state["messages"]
    tools = state["tools"]
    if tools:
        response = rag_answering_chain_tool.invoke(
            {
                "messages": messages,
                "prompt": state["prompt"],
            }
        )
    else:
        response = rag_answering_chain.invoke(
            {
                "messages": messages,
                "prompt": state["prompt"],
            }
        )
    return {"messages": response}
