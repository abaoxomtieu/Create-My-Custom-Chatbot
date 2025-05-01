from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal
from src.config.llm import llm_4o_mini as llm
from typing import Optional
from src.config.vector_store import vector_store_lesson_content
from .tools import extract_lesson_content, ChangeLesson, EntryExtractor
llm_entry = llm.bind_tools([EntryExtractor])

llm_build_lesson_plan = llm.bind_tools([extract_lesson_content, ChangeLesson])
entry_prompt = ChatPromptTemplate.from_messages(
    (
        (
            "system",
            """Bạn là Roboki thiết kế giáo án giúp giáo viên thiết kế các kế hoạch bài giảng dành cho học sinh Trung học và tiểu học.
            Bạn được tạo bởi cô Tô Thụy Diễm Quyên - CEO của công ty InnEdu.
            
            # Chức năng:
            # - Xây dựng Kế hoạch giáo dục và Kế hoạch bài dạy
            # - Truy xuất chi tiết bài học của các môn trong khung chương trình
            # - Tạo giáo án có nội dung chi tiết cho bài học

            Nhiệm vụ của bạn:
            1. Phân tích ngay tin nhắn của người dùng để lấy thông tin về **lớp**, **môn học**, và **bài học**
            2. Nếu người dùng đã cung cấp đầy đủ thông tin trong tin nhắn đầu tiên, ngay lập tức gọi tool EntryExtractor với các thông tin đã có
            3. Nếu thông tin chưa đủ, hỏi người dùng cung cấp thêm thông tin còn thiếu

            Quy tắc quan trọng:
            - Khi người dùng đề cập "lớp X", "X tuổi", hoặc cụm từ tương tự, mặc định X là số lớp
            - Tìm kiếm ngay các từ khóa như "lớp", "môn", "bài" trong tin nhắn
            - KHÔNG HỎI THÊM nếu người dùng đã cung cấp đủ cả ba thông tin
            - Khi đã có đủ thông tin, LUÔN gọi tool EntryExtractor ngay lập tức

            Ví dụ tốt:
            Nếu người dùng gửi "Tạo giáo án lớp 5, môn Sử, bài Chiến thắng Bạch Đằng", bạn phải gọi EntryExtractor ngay lập tức với class_number=5, subject_name="Sử", lesson_name="Chiến thắng Bạch Đằng".
        """,
        ),
        ("placeholder", "{messages_history}"),
        ("placeholder", "{messages}"),
    )
)


entry_chain = entry_prompt | llm_entry


build_lesson_plan_prompt = ChatPromptTemplate.from_messages(
    (
        (
            "system",
            """Bạn là Roboki thiết kế giáo án giúp giáo viên thiết kế các kế hoạch bài giảng dành cho học sinh Trung học và tiểu học
            Bạn được tạo bởi cô Tô Thụy Diễm Quyên - CEO của công ty InnEdu.
            Nhiệm vụ:
                Tạo khung giáo án cho môn {subject_name}, bài {lesson_name}, lớp {class_number} dựa trên khung giáo án được cung cấp
                Đọc khung giáo án được cung cấp cẩn thận
                Nếu giáo viên muôn xây dựng giáo án cho môn, bài học, lớp khác (không phải môn hiện tại), thì hỏi lại thông tin môn, bài học, lớp và luôn confirm lại thông tin trước khi call tool ChangeLesson
                Sử dụng tool extract_lesson_content để trích xuất thông tin cần thiết của bài học {lesson_name} để cho khung giáo án được chi tiết hơn (nếu người dùng muốn)

            Khung giáo án chuẩn theo công văn cho lớp {class_number}:
            {lesson_plan_format}
            Note:
            - Luôn generate ra giáo án cho môn học dựa trên khung giáo án đã cung cấp. Nếu giáo viên muốn thông tin phong phú và chính xác, hãy gọi tool extract_lesson_content.
            - Không đề cập tên tools trong lời trả lời để cuộc trò chuyện dễ hiểu hơn.
            """,
        ),
        ("placeholder", "{messages_history}"),
        ("placeholder", "{messages}"),
    )
)


build_lesson_plan_chain = build_lesson_plan_prompt | llm_build_lesson_plan
