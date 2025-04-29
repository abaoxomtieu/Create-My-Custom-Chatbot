import asyncio
from dotenv import load_dotenv
load_dotenv()
from src.agents.primary_chatbot.flow import lesson_plan_design_agent

# print(lesson_plan_design_agent.get_graph().draw_mermaid())

# user_query: str | AnyMessage
# messages_history: list
# document_id_selected: Optional[List]
# topic: str
# lesson_name: str
# subject_name: str
# class_number: int
# entry_response: str
# build_lesson_plan_response: AnyMessage


input_dict = {
    "user_query":"Tạo khung giáo án lớp 5, môn sử, bài Chiến thắng Bạch Đằng năm 938",
    "messages_history": [],
    "document_id_selected": None,
    "lesson_name": None,
    "subject_name": None,
    "class_number": None,
    "entry_response": None,
    "build_lesson_plan_response": None
}

async def main():
    response = await lesson_plan_design_agent.ainvoke(input_dict)
    print(response)
    print("===============================================")
    print(response["build_lesson_plan_response"][0].content)

asyncio.run(main())