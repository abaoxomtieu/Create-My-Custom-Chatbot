from src.config.vector_store import test_rag_vector_store as vector_store
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query
from langchain_core.documents import Document
import time

router = APIRouter(prefix="/vector-store")


@router.get("/get-documents")
async def get_documents(bot_id: Optional[str] = None):
    start = time.time()
    documents = await vector_store.asimilarity_search(
        "", 10000, filter={"bot_id": bot_id}
    )
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    return [doc.__dict__ for doc in documents]


@router.post("/add-documents")
async def add_documents(documents: List[Document], ids: List[str]):
    return await vector_store.aadd_documents(documents, ids=ids)


@router.delete("/delete-documents")
async def delete_documents(ids: List[str] = Query(None)):
    if not ids:
        return {"error": "No ids provided"}
    return await vector_store.adelete(ids=ids)
