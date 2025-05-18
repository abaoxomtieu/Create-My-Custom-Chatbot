from langchain_core.prompts import ChatPromptTemplate
from src.config.llm import llm_2_0 as llm

prompt_analyzed = ChatPromptTemplate.from_messages(
    [
        (
            "system",
        """
1. Mô tả vai trò.
    Bạn là một chuyên gia phân tích prompt 
2. Các bước thực hiện:
    2.1 Phân tích tiêu chí đánh giá prompt
    2.2 Đánh giá prompt dựa trên tiêu chí được cung cấp
    2.3 Phân tích ưu điểm
    2.4 Phân tích nhược điểm
    2.5 Nêu ra cách khắc phục
    2.6 Đề xuất những thứ cần bổ sung
    2.7 Viết lại prompt
        """,
        ),
        ("human",
         """
PROMPT: {prompt}
CRITERION: {criterion}
         """)
    ]
)

prompt_analyzed_creator_chain = prompt_analyzed | llm

prompt_create_advice = ChatPromptTemplate.from_messages(
    [
        (
            "system",
        """
Tôi sẽ cung cấp cho bạn luồng suy nghĩ và phân tích của một chuyên gia về phân tích prompt
Nhiệm vụ của bạn là tóm tắt lại luồng suy nghĩ đó để đưa ra nhận xét và lời khuyên cho người dùng
        """,
        ),
        ("human",
         """
THOUGHT: {thought}
         """)
    ]
)

prompt_create_advice_creator_chain = prompt_create_advice | llm
