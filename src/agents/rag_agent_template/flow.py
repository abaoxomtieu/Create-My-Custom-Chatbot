from langgraph.graph import StateGraph, START, END
from src.config.llm import llm_2_0
from .func import (
    State,
    trim_history,
    transform_query,
    retrieve_document,
    generate_answer_rag,
)
from langgraph.graph.state import CompiledStateGraph


class RAGAgentTemplate:
    def __init__(self):
        self.builder = StateGraph(State)

    @staticmethod
    def routing(state: State):
        pass

    def node(self):
        self.builder.add_node("trim_history", trim_history)
        self.builder.add_node("transform_query", transform_query)
        self.builder.add_node("retrieve_document", retrieve_document)
        self.builder.add_node("generate_answer_rag", generate_answer_rag)

    def edge(self):
        self.builder.add_edge(START, "trim_history")
        self.builder.add_edge("trim_history", "transform_query")
        self.builder.add_edge("transform_query", "retrieve_document")
        self.builder.add_edge("retrieve_document", "generate_answer_rag")
        self.builder.add_edge("generate_answer_rag", END)

    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile()


rag_agent_template_agent = RAGAgentTemplate()()
