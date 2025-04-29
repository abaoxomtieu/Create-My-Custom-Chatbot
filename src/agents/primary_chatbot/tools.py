from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal
from src.config.llm import llm_2_0 as llm
from typing import Optional
from src.config.vector_store import vector_store_lesson_content
from src.utils.logger import logger


@tool
async def extract_lesson_content(
    query_sentence: str, class_number: int, subject_name: str
) -> str:
    """Call vector store to retrieve documents based on query_sentence, class_number, subject_name
    
    
    Args:
        query_sentence (str): Query sentence
        class_number (int): Class number
        subject_name (str): Subject name
    Returns:
        str: Retrieved documents
    """
    filter = {
        "class_number": class_number,
        "subject_name": subject_name,
    }
    logger.info(f"Filter: {filter}")
    retriever = vector_store_lesson_content.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.3},
    )
    documents = await retriever.ainvoke(query_sentence, filter=filter)
    show_doc = " \n =============\n".join([doc.page_content for doc in documents])
    logger.info(f"Retrieved documents: {show_doc}")
    return {"documents": documents}


class ChangeLesson(BaseModel):
    """Khi người dùng đề cập đến môn, bài học, lớp khác thì call ChangeLesson tool. Hỏi người dùng confirm lại thông tin lesson_name, subject_name, class_number trước khi call ChangeLesson tool"""

    lesson_name: str = Field(description="Tên bài học")
    subject_name: str = Field(description="Tên môn học")
    class_number: int = Field(description="Số lớp học")


class EntryExtractor(BaseModel):
    """Khi thu thập đủ thông tin class_number, subject, lesson thì call EntryExtractor tool. Không cần hỏi confirm"""

    class_number: int = Field(description="Số lớp học")
    subject_name: str = Field(description="Môn học")
    lesson_name: str = Field(description="Bài học")
