from typing import TypedDict,Optional
from src.agents.prompt_analyzed.prompt import prompt_analyzed_creator_chain, prompt_create_advice_creator_chain

class State(TypedDict):
    prompt: str
    message: Optional[str]
    criterion: str
    thought: Optional[str]
    
def analyze_prompt(state:State):
    prompt = state.get("prompt","")
    criterion = state.get("criterion","")
    thought = prompt_analyzed_creator_chain.invoke({"prompt":prompt,"criterion":criterion}).content
    return {"thought":thought}

def create_advice_message(state:State):
    thought = state.get("thought","")
    message = prompt_create_advice_creator_chain.invoke({"thought":thought}).content
    return {"message":message}