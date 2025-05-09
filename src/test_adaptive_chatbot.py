import os
import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.agents.adaptive_chatbot.flow import adaptive_chatbot_agent
from src.utils.logger import logger

# Load environment variables
load_dotenv()

async def test_adaptive_chatbot_flow():
    """
    Test the adaptive chatbot flow with different scenarios
    """
    print("Testing adaptive chatbot flow...")
    
    # Print the flow diagram
    print("\n=== Flow Diagram ===")
    print(adaptive_chatbot_agent.get_graph().draw_mermaid())
    
    # Create test cases
    test_cases = [
        {
            "name": "New user query with no previous info",
            "state": {
                "user_message": "Tôi muốn tìm hiểu về machine learning",
                "session_id": "",
                "messages_history": [],
                "current_system_prompt": "",
                "user_profile": {}
            }
        },
        {
            "name": "Technical query from user",
            "state": {
                "user_message": "Có thể giải thích về cách hoạt động của transformer model trong NLP không?",
                "session_id": "test-session-1",
                "messages_history": [
                    {"content": "Xin chào", "type": "human"},
                    {"content": "Xin chào! Tôi có thể giúp gì cho bạn?", "type": "ai"}
                ],
                "current_system_prompt": "Bạn là một trợ lý AI hữu ích, trả lời câu hỏi người dùng một cách chính xác và đầy đủ.",
                "user_profile": {
                    "technical_level": "intermediate",
                    "preferred_style": "professional",
                    "interests": ["AI", "machine learning"]
                }
            }
        },
        {
            "name": "Simple, non-technical query",
            "state": {
                "user_message": "Thời tiết thế nào ở Hà Nội?",
                "session_id": "test-session-2",
                "messages_history": [],
                "current_system_prompt": "Bạn là một trợ lý AI thân thiện và hữu ích.",
                "user_profile": {}
            }
        }
    ]
    
    # Run test cases
    for i, test_case in enumerate(test_cases):
        print(f"\n\n=== Test Case {i+1}: {test_case['name']} ===")
        print(f"Input state: {test_case['state']}")
        
        try:
            # Add messages tuple if not present
            if "messages" not in test_case["state"]:
                test_case["state"]["messages"] = [("human", test_case["state"]["user_message"])]
                
            # Execute the flow with the test state
            result = await adaptive_chatbot_agent.ainvoke(test_case['state'])
            
            # Display the result
            print("\nResult:")
            for key, value in result.items():
                if key == "messages_history":
                    print(f"  {key}: [... {len(value)} messages ...]")
                elif key == "analysis_result":
                    print(f"  {key}: {value}")
                elif key == "user_profile":
                    print(f"  {key}: {value}")
                elif key == "bot_message" and value:
                    print(f"  {key}: {value[:100]}... (truncated)")
                else:
                    print(f"  {key}: {value}")
                    
            print("\nFlow execution successful!")
        except Exception as e:
            print(f"Error executing flow: {e}")
    
    print("\n=== All tests completed ===")

async def test_specific_node():
    """
    Test a specific node in the flow
    """
    from src.agents.adaptive_chatbot.func import analyze_user_request, generate_probing_questions, update_system_prompt
    
    # Test the analyze_user_request node
    print("\n=== Testing analyze_user_request node ===")
    state = {
        "user_message": "Tôi muốn hiểu sâu hơn về machine learning và các thuật toán",
        "session_id": "test-session",
        "messages_history": [],
        "current_system_prompt": "Bạn là một trợ lý AI hữu ích.",
        "user_profile": {},
        "messages": [("human", "Tôi muốn hiểu sâu hơn về machine learning và các thuật toán")]
    }
    
    try:
        analysis_result = await analyze_user_request(state)
        print("analyze_user_request node result:")
        for key, value in analysis_result.items():
            if key == "analysis_result":
                print(f"  {key}: {value}")
            elif key == "prompt_needs_update":
                print(f"  {key}: {value}")
            elif key == "probing_questions_needed":
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error in analyze_user_request node: {e}")
    
    # Test the generate_probing_questions node
    print("\n=== Testing generate_probing_questions node ===")
    state = {
        "user_message": "Tôi muốn học machine learning",
        "session_id": "test-session",
        "messages_history": [],
        "current_system_prompt": "Bạn là một trợ lý AI hữu ích.",
        "user_profile": {},
        "analysis_result": {
            "intent": "learn_about_topic",
            "keywords": ["machine learning"],
            "prompt_needs_update": True,
            "probing_questions_needed": True
        },
        "messages": [("human", "Tôi muốn học machine learning")]
    }
    
    try:
        probing_result = await generate_probing_questions(state)
        print("generate_probing_questions node result:")
        if "probing_questions" in probing_result:
            print(f"  probing_questions: {probing_result['probing_questions']}")
    except Exception as e:
        print(f"Error in generate_probing_questions node: {e}")
        
    # Test the update_system_prompt node
    print("\n=== Testing update_system_prompt node ===")
    state = {
        "user_message": "Tôi muốn học machine learning",
        "session_id": "test-session",
        "messages_history": [],
        "current_system_prompt": "Bạn là một trợ lý AI hữu ích.",
        "user_profile": {
            "technical_level": "beginner",
            "preferred_style": "friendly",
            "interests": ["AI", "machine learning"]
        },
        "analysis_result": {
            "intent": "learn_about_topic",
            "keywords": ["machine learning"],
            "prompt_needs_update": True,
            "probing_questions_needed": False
        },
        "messages": [("human", "Tôi muốn học machine learning")]
    }
    
    try:
        prompt_result = await update_system_prompt(state)
        print("update_system_prompt node result:")
        if "updated_system_prompt" in prompt_result:
            print(f"  updated_system_prompt: {prompt_result['updated_system_prompt']}")
    except Exception as e:
        print(f"Error in update_system_prompt node: {e}")

if __name__ == "__main__":
    # You can choose which test to run:
    # 1. Test the entire flow
    # 2. Test specific nodes
    
    # Run the async tests
    print("Choose a test to run:")
    print("1. Test the entire flow")
    print("2. Test specific nodes")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(test_adaptive_chatbot_flow())
    elif choice == "2":
        asyncio.run(test_specific_node())
    else:
        print("Invalid choice. Please run again with a valid option.") 