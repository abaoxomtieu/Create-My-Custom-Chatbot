from typing import TypedDict, Optional, List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langchain_core.documents import Document
from langchain_core.messages import trim_messages, AnyMessage
from src.utils.helper import (
    fake_token_counter,
    convert_list_context_source_to_str,
    convert_message,
)
import os
from .prompt import transform_query_chain, rag_answering_chain, GenerateAnswer
from src.config.vector_store import test_rag_vector_store
from src.utils.logger import logger


class State(TypedDict):
    messages: AnyMessage
    messages_history: list[AnyMessage]
    documents: list[Document]
    selected_ids: Optional[List]
    selected_documents: Optional[List[Document]]
    llm_response: str
    filter: dict


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
        max_tokens=int(os.getenv("HISTORY_TOKEN_LIMIT", 2000)),
        start_on="human",
        end_on="ai",
        include_system=False,
        allow_partial=False,
    )
    return {"messages_history": chat_message_history}


async def transform_query(state: State):
    # Handle image-based queries
    message = state["messages"]
    # Extract the text part from the message content
    if isinstance(message["content"], list):
        for content_item in message["content"]:
            if content_item["type"] == "text":
                question = content_item["text"]
                break
    else:
        # Handle text-only queries
        question = message["content"]

    history = state.get("messages_history", [])
    transform_response = await transform_query_chain.ainvoke(
        {"question": question, "messages_history": history}
    )
    logger.info(f"Transform response: {transform_response}")

    if isinstance(message["content"], list):
        return {
            "messages": {
                "role": "user",
                "content": [
                    {"type": "text", "text": transform_response.content},
                    {
                        "type": "image",
                        "source_type": "url",
                        "url": message["content"][1]["url"],
                    },
                ],
            }
        }
    else:
        return {
            "messages": {
                "role": "user",
                "content": transform_response.content,
            }
        }


async def retrieve_document(state: State):
    messages = state["messages"]
    if isinstance(messages["content"], list):
        question = messages["content"][0]["text"]
    else:
        question = messages["content"]
    filter = state.get("filter", None)
    logger.info(f"Filter: {filter}")
    retriever = test_rag_vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.3},
    )
    documents = await retriever.ainvoke(question)
    show_doc = " \n =============\n".join([doc.page_content for doc in documents])
    # logger.info(f"Retrieved documents: {show_doc}")
    return {"documents": documents}


async def generate_answer_rag(state: State):
    documents = state["documents"]
    history = state["messages_history"]
    messages = state["messages"]
    if documents:
        context_str = convert_list_context_source_to_str(documents)
    else:
        context_str = "Không tìm thấy tài liệu"

    gen_answer_response = await rag_answering_chain.ainvoke(
        {
            "context": context_str,
            "messages_history": history,
            "messages": [messages],
        }
    )

    # Convert documents to dictionary format for JSON serialization
    documents = [doc.__dict__ for doc in documents]
    if documents:
        print("documents", documents[0])

    selected_ids = [doc["id"] for doc in documents] if documents else []

    return {
        "llm_response": gen_answer_response.content,
        "selected_ids": selected_ids,
        "selected_documents": documents,
    }
