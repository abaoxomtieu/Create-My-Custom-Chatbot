from langchain_core.tools import tool
from src.config.vector_store import test_rag_vector_store
from src.utils.helper import convert_list_context_source_to_str
from src.utils.logger import logger
from langchain_core.runnables import RunnableConfig


@tool
def retrieve_document(query: str, config: RunnableConfig):
    """Ưu tiên truy xuất tài liệu từ vector store nếu câu hỏi liên quan đến vai trò của chatbot.
    

    Args:
        query (str): Câu truy vấn của người dùng bằng tiếng Việt
    Returns:
        str: Retrieved documents
    """
    configuration = config.get("configurable", {})
    bot_id = configuration.get("bot_id", None)
    if not bot_id:
        logger.error("Bot ID is not found")
        return {"context_str": "", "selected_documents": [], "selected_ids": []}
    retriever = test_rag_vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.3},
    )
    documents = retriever.invoke(query, filter={"bot_id": bot_id})
    selected_documents = [doc.__dict__ for doc in documents]
    selected_ids = [doc["id"] for doc in selected_documents]
    context_str = convert_list_context_source_to_str(documents)

    return {
        "context_str": context_str,
        "selected_documents": selected_documents,
        "selected_ids": selected_ids,
    }
