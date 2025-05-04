from langgraph.graph import StateGraph, START, END
from .func import State, create_prompt_assistant, complete_prompt, trim_history
from src.utils.helper import create_tool_node_with_fallback
from langgraph.prebuilt import tools_condition
from src.utils.logger import logger
from langgraph.graph.state import CompiledStateGraph



class PromptEngineerAssistantFlow:
    def __init__(self):
        self.builder = StateGraph(State)

    @staticmethod
    def after_create_prompt_assistant_chain(state: State):
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        if tool_calls:
            if tool_calls[0]["name"] == "prompt_create_complete":
                logger.info("Prompt created")
                return "complete_prompt"
        raise ValueError("No tool calls found")

    def node(self):
        self.builder.add_node("trim_history", trim_history)
        self.builder.add_node("create_prompt_assistant", create_prompt_assistant)
        self.builder.add_node("complete_prompt", complete_prompt)

    def edge(self):
        self.builder.add_edge(START, "trim_history")
        self.builder.add_edge("trim_history", "create_prompt_assistant")
        self.builder.add_conditional_edges(
            "create_prompt_assistant",
            self.after_create_prompt_assistant_chain,
            {
                "complete_prompt": "complete_prompt",
                END: END,
            },
        )
        self.builder.add_edge("complete_prompt", END)

    def __call__(self):
        self.node()
        self.edge()
        return self.builder.compile()

prompt_engineer_assistant_agent = PromptEngineerAssistantFlow()()