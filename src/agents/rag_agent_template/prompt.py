from langchain_core.prompts import ChatPromptTemplate
from src.config.llm import get_llm
from .tools import retrieve_document

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
