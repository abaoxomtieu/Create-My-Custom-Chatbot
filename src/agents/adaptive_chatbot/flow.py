from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from .data import State
from .func import (
    initialize_state,
    analyze_user_request,
    generate_probing_questions,
    update_user_profile,
    update_system_prompt,
    generate_bot_response,
    process_return_value,
    trim_history,
)
from src.utils.logger import logger


class AdaptiveChatbotAgent:
    def __init__(self):
        self.builder = StateGraph(State)

    @staticmethod
    def after_analysis(state: State):
        """
        Determine the next step after analyzing the user request.
        
        Args:
            state: Current state
            
        Returns:
            Next node to execute
        """
        if state.get("probing_questions_needed", False):
            logger.info("Analysis indicates probing questions are needed")
            return "generate_probing_questions"
        elif state.get("prompt_needs_update", False):
            logger.info("Analysis indicates prompt update is needed")
            return "update_user_profile"
        else:
            logger.info("No special handling needed, proceeding to response generation")
            return "generate_bot_response"

    @staticmethod
    def after_probing_questions(state: State):
        """
        Determine the next step after generating probing questions.
        
        Args:
            state: Current state
            
        Returns:
            Next node to execute
        """
        if state.get("probing_questions") and len(state.get("probing_questions", [])) > 0:
            logger.info("Probing questions generated, returning to user")
            return END
        else:
            logger.info("No probing questions generated, proceeding to response generation")
            return "update_user_profile"

    def node(self):
        """Add nodes to the graph."""
        # Add all the nodes
        self.builder.add_node("initialize_state", initialize_state)
        self.builder.add_node("analyze_user_request", analyze_user_request)
        self.builder.add_node("generate_probing_questions", generate_probing_questions)
        self.builder.add_node("update_user_profile", update_user_profile)
        self.builder.add_node("update_system_prompt", update_system_prompt)
        self.builder.add_node("generate_bot_response", generate_bot_response)
        self.builder.add_node("process_return_value", process_return_value)
        self.builder.add_node("trim_history", trim_history)

    def edge(self):
        """Define edges between nodes."""
        # Define the edges
        self.builder.add_edge(START, "initialize_state")
        self.builder.add_edge("initialize_state", "analyze_user_request")
        
        # After analysis, determine next steps
        self.builder.add_conditional_edges(
            "analyze_user_request",
            self.after_analysis,
            {
                "generate_probing_questions": "generate_probing_questions",
                "update_user_profile": "update_user_profile",
                "generate_bot_response": "generate_bot_response",
            },
        )
        
        # After generating probing questions
        self.builder.add_conditional_edges(
            "generate_probing_questions",
            self.after_probing_questions,
            {
                END: END,
                "update_user_profile": "update_user_profile",
            },
        )
        
        # Standard flow path
        self.builder.add_edge("update_user_profile", "update_system_prompt")
        self.builder.add_edge("update_system_prompt", "generate_bot_response")
        self.builder.add_edge("generate_bot_response", "process_return_value")
        self.builder.add_edge("process_return_value", "trim_history")
        self.builder.add_edge("trim_history", END)

    def __call__(self) -> CompiledStateGraph:
        """
        Build and compile the graph.
        
        Returns:
            Compiled graph
        """
        self.node()
        self.edge()
        return self.builder.compile()


# Create and compile the agent graph
adaptive_chatbot_agent = AdaptiveChatbotAgent()() 