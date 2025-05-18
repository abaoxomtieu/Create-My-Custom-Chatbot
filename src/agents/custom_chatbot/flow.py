from langgraph.graph import StateGraph, START, END
from src.config.llm import llm_2_0
from .func import State
from langgraph.graph.state import CompiledStateGraph
from src.agents.react_agent.flow import react_agent
from langchain_core.messages import ToolMessage,AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from src.agents.custom_chatbot.func import create_prompt,save_prompt
checkpointer = InMemorySaver()


class CustomChatBot:
    def __init__(self):
        self.builder = StateGraph(State)

    @staticmethod
    def is_enough_information(state: State):
        messages = state.get("messages", "")
        for idx,message in enumerate(messages):
            if isinstance(message, ToolMessage):
                return "create_prompt"
        return "END"

    def node(self):
        self.builder.add_node("react_agent", react_agent)
        self.builder.add_node("create_prompt", create_prompt)
        self.builder.add_node("save_prompt", save_prompt)

    def edge(self):
        self.builder.add_edge(START, "react_agent")
        self.builder.add_conditional_edges(
            "react_agent",
            self.is_enough_information,
            {"create_prompt": "create_prompt", "END": END},
        )
        self.builder.add_edge("create_prompt","save_prompt")
        self.builder.add_edge("save_prompt",END)

    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile(checkpointer)


custom_chatbot = CustomChatBot()()