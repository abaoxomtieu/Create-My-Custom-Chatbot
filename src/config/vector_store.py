from .llm import embeddings
import os
from langchain_pinecone import PineconeVectorStore

API_PINCONE_KEY = os.getenv("PINECONE_API_KEY")

test_rag_vector_store = PineconeVectorStore(
    index_name="rag-vector-store",
    embedding=embeddings,
    pinecone_api_key=API_PINCONE_KEY,
)
