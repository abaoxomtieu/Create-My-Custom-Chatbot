from langgraph.graph import StateGraph, START, END
from src.config.llm import llm_2_0
from .func import State
from langgraph.graph.state import CompiledStateGraph
from src.agents.prompt_analyzed.flow import analyze_prompt, analyze_agent
from src.agents.react_agent.prompt import ReAgent_prompt
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, List

def enough_information(info:str):
    """
    gọi tool này sau khi hoàn tất quá trình thu thập thông tin cần thiết
    Args:
        info (str): Thông tin đã thu thập được
    """
    print(info)
    return "Created successful"

react_agent = create_react_agent(
    model=llm_2_0,
    tools=[enough_information],
    prompt=ReAgent_prompt,

)
