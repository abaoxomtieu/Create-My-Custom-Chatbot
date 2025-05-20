from langchain_core.prompts import ChatPromptTemplate
from src.config.llm import get_llm
from pydantic import BaseModel, Field
from typing import Optional
from .tools import retrieve_document

test_prompt = """
Bạn là một hướng dẫn viên du lịch AI chuyên nghiệp.
Vai trò của bạn:
- Hỗ trợ giải đáp người dùng về các vấn đề về du lịch
- Lên kế hoạch du lịch cho người dùng
- Cho phép người dùng hỏi đáp về dịa điểm dựa trên hình ảnh

Quy trình trả lời:
- Luôn bắt đầu bằng một lời chào thân thiện cho người dùng
- Nếu người dùng hỏi những câu ngoài lề thì điều hướng hoặc cho họ ví dụ về các câu hỏi trong khả năng của bạn. Nhưng lịch sự
- Dựa vào ngữ cảnh truy xuất đề trả lời cho người dùng.


Sử dụng tool `retrieve_document` để truy xuất tài liệu(call tool sau 1 lần hỏi, đừng hỏi quá nhiều)
"""

rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{prompt}"),
        ("placeholder", "{messages}"),
    ]
)

def get_rag_chains(model_name: str):
    llm = get_llm(model_name)
    llm_rag = llm.bind_tools([retrieve_document])
    rag_answering_chain_tool = rag_prompt | llm_rag
    rag_answering_chain = rag_prompt | llm
    return rag_answering_chain_tool, rag_answering_chain
