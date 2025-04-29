from pydantic import BaseModel, Field


class TestInfo(BaseModel):
    subject: str = Field(description="The subject of the test")
    level: str = Field(description="The educational level of the test")
    total_questions: int = Field(description="Total number of questions in the test")
    duration: str = Field(description="Duration of the test")


class Question(BaseModel):
    correct: bool = Field(description="Whether the student answered correctly")
    question: str = Field(description="The question text")


class LessonResult(BaseModel):
    chapter_name: str = Field(description="Name of the chapter")
    chapter_number: str = Field(description="Unique identifier for the chapter")
    questions: list[Question] = Field(description="List of questions in this chapter")


class TestResultsBody(BaseModel):
    test_info: TestInfo = Field(description="General information about the test")
    results: list[LessonResult] = Field(
        description="Results for each lesson in the test"
    )
    language: str = Field(description="Language of the test")

    model_config = {
        "json_schema_extra": {
            "example": {
                "test_info": {
                    "subject": "Sử",
                    "level": "Cấp 2",
                    "total_questions": 20,
                    "duration": "60 minutes",
                },
                "language": "Vietnamese",
                "results": [
                    {
                        "chapter_name": "Chương 1: Lịch sử Việt Nam từ thế kỉ X đến thế kỉ XIX",
                        "chapter_number": "L01",
                        "questions": [
                            {
                                "correct": True,
                                "question": "Nhận thức lịch sử là gì?",
                            },
                            {"correct": True, "question": "Sử học là gì?"},
                            {
                                "correct": True,
                                "question": "Đối tượng nghiên cứu của Sử học là",
                            },
                            {
                                "correct": True,
                                "question": "Các chức năng của Sử học bao gồm",
                            },
                            {
                                "correct": False,
                                "question": "Nội dung nào sau đây không phải là nhiệm vụ của Sử học?",
                            },
                            {
                                "correct": True,
                                "question": "Trong nghiên cứu lịch sử, các nhà sử học cần phải tuân thủ những nguyên tắc cơ bản nào?",
                            },
                            {"correct": True, "question": "Sử liệu là gì?"},
                            {
                                "correct": True,
                                "question": "Căn cứ vào mối liên hệ với sự vật, hiện tượng được nghiên cứu và giá trị thông tin, sử liệu được chia thành những loại nào?",
                            },
                            {
                                "correct": False,
                                "question": "Căn cứ vào dạng thức tồn tại, sử liệu không bao gồm nhóm nào sau đây?",
                            },
                            {
                                "correct": True,
                                "question": "Rìu tay Núi Đọ (Thanh Hóa) thuộc loại hình sử liệu nào?",
                            },
                            {
                                "correct": True,
                                "question": "Hai phương pháp cơ bản trong nghiên cứu lịch sử là",
                            },
                            {
                                "correct": True,
                                "question": "Nội dung nào sau đây phản ánh điểm giống nhau giữa phương pháp lịch sử và phương pháp logic trong nghiên cứu lịch sử?",
                            },
                            {
                                "correct": False,
                                "question": "Hiện thực lịch sử có điểm gì khác biệt so với nhận thức lịch sử?",
                            },
                        ],
                    },
                    {
                        "chapter_name": "Chương 2: Lịch sử Việt Nam từ thế kỉ X đến thế kỉ XIX",
                        "chapter_number": "L02",
                        "questions": [
                            {
                                "correct": True,
                                "question": "Chọn cụm từ thích hợp điền vào chỗ trống để hoàn thành khái nhiệm sau: '…… là những hiểu biết của con người về các lĩnh vực liên quan đến lịch sử, hình thành qua quá trình học tập, khám phá, nghiên cứu và trải nghiệm'",
                            },
                            {
                                "correct": True,
                                "question": "Nội dung nào sau đây là một trong những vai trò của tri thức lịch sử?",
                            },
                            {
                                "correct": True,
                                "question": "Tri thức lịch sử được hình thành qua những quá trình nào sau đây?",
                            },
                            {
                                "correct": False,
                                "question": "Nội dung nào sau đây là một trong những ý nghĩa của tri thức lịch sử đối với con người?",
                            },
                            {
                                "correct": True,
                                "question": "Tri thức lịch sử không đem lại ý nghĩa nào sau đây đối với mỗi cá nhân và xã hội?",
                            },
                            {
                                "correct": False,
                                "question": "Những bài học kinh nghiệm trong lịch sử có giá trị như thế nào đối với cuộc sống hiện tại và tương lai của con người?",
                            },
                        ],
                    },
                ],
            }
        }
    }
