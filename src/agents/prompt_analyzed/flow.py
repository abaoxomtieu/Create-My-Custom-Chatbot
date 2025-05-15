from langgraph.graph import StateGraph, START, END
from src.config.llm import llm_2_0
from .func import State,analyze_prompt, create_advice_message
from langgraph.graph.state import CompiledStateGraph


class PromptAnalyzeAgent:
    def __init__(self):
        self.builder = StateGraph(State)

    def node(self):
        self.builder.add_node("analyze",analyze_prompt)
        self.builder.add_node("advice",create_advice_message)

    def edge(self):
        self.builder.add_edge(START,"analyze")
        self.builder.add_edge("analyze","advice")
        self.builder.add_edge("advice",END)
        pass
    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile()
    
analyze_agent = PromptAnalyzeAgent()()
