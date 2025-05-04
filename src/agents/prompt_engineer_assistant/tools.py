from langchain_core.tools import tool


@tool
def prompt_create_complete(
    role: str,
    context: str,
    input_values: str,
    instructions: str,
    guidelines: str,
    output_format: str,
):
    """Call prompt_create_complete tool when collect all details for prompt
    
    Args:
        role (str): Role
        context (str): Context
        input_values (str): Input values
        instructions (str): Instructions
        guidelines (str): Guidelines
        output_format (str): Output format
    """
