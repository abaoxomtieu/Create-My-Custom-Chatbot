# from langchain_mongodb import MongoDBAtlasVectorSearch
# from pymongo import MongoClient
from .llm import embeddings
import os
from langchain_pinecone import PineconeVectorStore

API_PINCONE_KEY = os.getenv("PINECONE_API_KEY")
index_lesson_content = "chatbot-vector-store"

vector_store_lesson_content = PineconeVectorStore(
    index_name=index_lesson_content,
    embedding=embeddings,
    pinecone_api_key=API_PINCONE_KEY,
)

test_rag_vector_store = PineconeVectorStore(
    index_name="rag-vector-store",
    embedding=embeddings,
    pinecone_api_key=API_PINCONE_KEY,
)