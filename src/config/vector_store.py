# from langchain_mongodb import MongoDBAtlasVectorSearch
# from pymongo import MongoClient
from .llm import embeddings
import os
from langchain_pinecone import PineconeVectorStore

# client = MongoClient(os.getenv("MONGO_CONNECTION_STR"))

# DB_NAME = os.getenv("DB_NAME")
# COLLECTION_NAME = os.getenv("COLLECTION_NAME")
# ATLAS_VECTOR_CHATBOT_INDEX_NAME = os.getenv("ATLAS_VECTOR_CHATBOT_INDEX_NAME")
# ATLAS_VECTOR_TUTOR_INDEX_NAME = os.getenv("ATLAS_VECTOR_TUTOR_INDEX_NAME")

# MONGODB_COLLECTION_CHATBOT = client[DB_NAME][ATLAS_VECTOR_CHATBOT_INDEX_NAME]
# MONGODB_COLLECTION_TUTOR = client[DB_NAME][ATLAS_VECTOR_TUTOR_INDEX_NAME]

# vector_store_chatbot = MongoDBAtlasVectorSearch(
#     collection=MONGODB_COLLECTION_CHATBOT,
#     embedding=embeddings,
#     index_name=ATLAS_VECTOR_CHATBOT_INDEX_NAME,
#     relevance_score_fn="cosine",
# )
# vector_store_tutor = MongoDBAtlasVectorSearch(
#     collection=MONGODB_COLLECTION_TUTOR,
#     embedding=embeddings,
#     index_name=ATLAS_VECTOR_TUTOR_INDEX_NAME,
#     relevance_score_fn="cosine",
# )
API_PINCONE_KEY = os.getenv("PINECONE_API_KEY")
# index_lesson_content = "lesson-content-vector-store"
index_lesson_content = "chatbot-vector-store"

vector_store_lesson_content = PineconeVectorStore(
    index_name=index_lesson_content,
    embedding=embeddings,
    pinecone_api_key=API_PINCONE_KEY,
)
