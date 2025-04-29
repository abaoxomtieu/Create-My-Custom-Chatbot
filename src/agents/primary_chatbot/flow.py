from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition

from .func import State, trim_history, entry, build_lesson_plan, change_lesson
from src.utils.helper import create_tool_node_with_fallback
from .tools import EntryExtractor, extract_lesson_content, ChangeLesson
from src.utils.logger import logger


class LessonPlanDesignAgent:
    def __init__(self):
        self.builder = StateGraph(State)
        self.lesson_plan_design_tools = [extract_lesson_content]

    @staticmethod
    def check_existed_entry_info(state: State):
        if (
            not state["class_number"]
            or not state["subject_name"]
            or not state["lesson_name"]
        ):
            return "entry"
        else:
            return "build_lesson_plan"

    @staticmethod
    def after_entry(state: State):
        if (
            not state["class_number"]
            or not state["subject_name"]
            or not state["lesson_name"]
        ):
            return END
        else:
            return "build_lesson_plan"

    @staticmethod
    def after_build_lesson_plan(state: State):
        logger.info("Build lesson plan response")
        route = tools_condition(state, "build_lesson_plan_response")
        if route == END:
            return END
        tool_calls = state["build_lesson_plan_response"][-1].tool_calls
        if tool_calls:
            if tool_calls[0]["name"] == "ChangeLesson":
                logger.info("Change Lesson")
                return "change_lesson"
            logger.info("Extract Lesson Content")
            return "lesson_plan_design_tools"
        raise ValueError("No tool calls found")

    def node(self):
        self.builder.add_node("trim_history", trim_history)
        self.builder.add_node("entry", entry)
        self.builder.add_node("build_lesson_plan", build_lesson_plan)
        self.builder.add_node("change_lesson", change_lesson)
        self.builder.add_node(
            "lesson_plan_design_tools",
            create_tool_node_with_fallback(self.lesson_plan_design_tools),
        )

    def edge(self):
        self.builder.add_edge(START, "trim_history")
        self.builder.add_conditional_edges(
            "trim_history",
            self.check_existed_entry_info,
            {
                "entry": "entry",
                "build_lesson_plan": "build_lesson_plan",
            },
        )
        self.builder.add_conditional_edges(
            "entry",
            self.after_entry,
            {
                END: END,
                "build_lesson_plan": "build_lesson_plan",
            },
        )
        self.builder.add_conditional_edges(
            "build_lesson_plan",
            self.after_build_lesson_plan,
            {
                END: END,
                "change_lesson": "change_lesson",
                "lesson_plan_design_tools": "lesson_plan_design_tools",
            },
        )
        self.builder.add_edge("change_lesson", "build_lesson_plan")
        self.builder.add_edge("lesson_plan_design_tools", "build_lesson_plan")

    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile()


lesson_plan_design_agent = LessonPlanDesignAgent()()

#
