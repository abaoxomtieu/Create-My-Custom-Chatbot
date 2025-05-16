from langchain_core.tools import tool


@tool
def prompt_create_complete(
    prompt:str
):
    """Call prompt_create_complete tool when collect all details for prompt. Always ask for confirm from user before call tool

    Args:
        role (str): Role
        context (str): Context
        input_values (str): Input values
        instructions (str): Instructions
        guidelines (str): Guidelines
        output_format (str): Output format
    """
