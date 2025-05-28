from langchain_core.prompts import ChatPromptTemplate
from src.config.llm import get_llm
from .tools import retrieve_document

template_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{prompt}"),
        ("placeholder", "{messages}"),
    ]
)
