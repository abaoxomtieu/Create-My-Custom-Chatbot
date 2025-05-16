from langchain_core.tools import tool
from src.config.vector_store import test_rag_vector_store
from src.utils.helper import convert_list_context_source_to_str
from src.utils.logger import logger


@tool
def retrieve_document(query: str):
    """Call vector store to retrieve documents based on query

    Args:
        query (str): Query
    Returns:
        str: Retrieved documents
    """

    retriever = test_rag_vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.3},
    )
    documents = retriever.invoke(query)
    selected_documents = [doc.__dict__ for doc in documents]
    selected_ids = [doc["id"] for doc in selected_documents]
    context_str = convert_list_context_source_to_str(documents)

    return {
        "context_str": context_str,
        "selected_documents": selected_documents,
        "selected_ids": selected_ids,
    }
