import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)
from src.agents.prompt_analyzed.flow import analyze_agent

criterion = """
Hướng Dẫn Viết Instruction Mô Tả Hoạt Động Của Chatbot 

1. Giới Thiệu 

Instruction (hướng dẫn) là một phần quan trọng trong quá trình xây dựng chatbot, giúp mô tả cách chatbot phản hồi và hoạt động theo mục tiêu đề ra. Tài liệu này hướng dẫn cách viết instruction hiệu quả để tối ưu hóa hoạt động của chatbot. 

2. Nguyên Tắc Viết Instruction 

Cụ thể và rõ ràng: Mô tả hành vi của chatbot một cách chi tiết. 

Ngắn gọn nhưng đầy đủ: Tránh viết dài dòng, tập trung vào mục tiêu chính. 

Sử dụng ngôn ngữ tự nhiên: Viết hướng dẫn dễ hiểu, tránh thuật ngữ quá chuyên môn. 

Tính nhất quán: Đảm bảo các hướng dẫn không mâu thuẫn với nhau. 

Tính linh hoạt: Hướng dẫn cần đủ linh hoạt để chatbot có thể xử lý nhiều tình huống khác nhau. 

3. Các Thành Phần Của Instruction 

Instruction cần có các phần chính sau: 

3.1. Mô Tả Mục Tiêu Chatbot 

Xác định mục tiêu chính của chatbot (ví dụ: hỗ trợ khách hàng, tư vấn sản phẩm, trợ lý học tập...) 

Định nghĩa rõ chatbot sẽ giải quyết vấn đề gì cho người dùng. 

Ví dụ:  

Chatbot này được thiết kế để hỗ trợ khách hàng trong việc đặt hàng trực tuyến, giải đáp thắc mắc về sản phẩm và hỗ trợ sau bán hàng. 

3.2. Định Nghĩa Vai Trò Của Chatbot 

Chatbot hoạt động như thế nào? (trợ lý ảo, tổng đài tự động, chuyên gia tư vấn...) 

Có giọng điệu giao tiếp như thế nào? (thân thiện, trang trọng, hài hước...) 

Ví dụ:  

Chatbot sẽ đóng vai trò như một nhân viên hỗ trợ khách hàng, sử dụng giọng điệu thân thiện và chuyên nghiệp để giải đáp các câu hỏi. 

3.3. Quy Tắc Phản Hồi 

Xác định cách chatbot phản hồi trong các trường hợp khác nhau. 

Ví dụ về phản hồi trong các tình huống cụ thể:  

Khi khách hàng hỏi về sản phẩm:  

Nếu khách hàng hỏi về sản phẩm, cung cấp mô tả ngắn gọn kèm theo giá cả và đường dẫn đến trang sản phẩm. 

Khi chatbot không hiểu câu hỏi:  

Nếu chatbot không hiểu câu hỏi, đề nghị khách hàng diễn đạt lại hoặc cung cấp từ khóa liên quan. 

Khi chatbot nhận phản hồi tiêu cực:  

Nếu khách hàng phản hồi tiêu cực, chatbot nên xin lỗi và đề nghị hướng giải quyết phù hợp. 

3.4. Xử Lý Dữ Liệu Đầu Vào 

Xác định chatbot sẽ xử lý dữ liệu đầu vào như thế nào. 

Ví dụ:  

- Nếu khách hàng nhập câu hỏi dài, chatbot sẽ tóm tắt và hỏi lại để xác nhận. 

- Nếu khách hàng nhập sai chính tả, chatbot sẽ tự động đề xuất từ đúng. 

3.5. Giới Hạn Của Chatbot 

Xác định những nội dung chatbot không thể xử lý. 

Ví dụ:  

Chatbot không hỗ trợ các vấn đề liên quan đến bảo mật tài khoản hoặc xử lý khiếu nại phức tạp. Người dùng sẽ được hướng dẫn liên hệ với bộ phận hỗ trợ khách hàng. 

3.6. Luồng Hội Thoại Cơ Bản 

Xây dựng kịch bản hội thoại điển hình. 

Ví dụ: Người dùng: Tôi muốn biết giá sản phẩm X. Chatbot: Sản phẩm X hiện có giá 500.000 VND. Bạn có muốn đặt hàng ngay không? Người dùng: Có. Chatbot: Bạn vui lòng cung cấp địa chỉ giao hàng. 

4. Hướng Dẫn Viết Instruction Cho Các Loại Chatbot Khác Nhau 

4.1. Chatbot Hỗ Trợ Khách Hàng 

Phản hồi nhanh chóng, cung cấp thông tin chính xác. 

Hỗ trợ giải quyết vấn đề của khách hàng hiệu quả. 

Ví dụ instruction:  

- Trả lời các câu hỏi về chính sách bảo hành, đổi trả trong vòng 3 giây. 

- Nếu khách hàng yêu cầu hỗ trợ chuyên sâu, hướng dẫn họ liên hệ tổng đài viên. 

4.2. Chatbot Giáo Dục 

Cung cấp thông tin chi tiết, dễ hiểu. 

Tạo môi trường học tập thân thiện. 

Ví dụ instruction:  

- Giải thích khái niệm bằng cách sử dụng ví dụ thực tế. 

- Nếu học sinh yêu cầu bài tập, cung cấp bài tập kèm theo gợi ý giải. 

4.3. Chatbot Tư Vấn Sản Phẩm 

Giới thiệu sản phẩm theo nhu cầu khách hàng. 

Hướng dẫn khách hàng đặt hàng nhanh chóng. 

Ví dụ instruction:  

- Khi khách hàng hỏi về một sản phẩm, cung cấp hình ảnh, giá cả và các tính năng chính. 

- Nếu khách hàng chưa quyết định, đề xuất sản phẩm tương tự dựa trên nhu cầu của họ. 

5. Cách Kiểm Tra Và Cải Tiến Instruction 

Thử nghiệm thực tế: Kiểm tra phản hồi của chatbot với nhiều loại câu hỏi. 

Thu thập phản hồi: Hỏi người dùng về trải nghiệm sử dụng chatbot. 

Cập nhật định kỳ: Điều chỉnh instruction dựa trên dữ liệu thực tế. 

6. Kết Luận 

Viết instruction hiệu quả giúp chatbot hoạt động mượt mà, chính xác và đáp ứng nhu cầu người dùng. Hãy luôn kiểm tra, thử nghiệm và cập nhật để chatbot ngày càng thông minh hơn! 

"""

res = analyze_agent.invoke(
    {
        "prompt": """Bạn là một người hướng dẫn khoa học dữ liệu Python. Bạn đang giúp đỡ Alex, một nhà phát triển phần mềm. Phong cách giao tiếp của bạn nên ngắn gọn và trực tiếp.\n\nMục tiêu chính của bạn là giúp Alex cung cấp hướng dẫn về các dự án phân tích dữ liệu Python. Đặc biệt tập trung vào các lĩnh vực chính sau: Cấu 
trúc dự án Python, Quy trình làm việc phân tích dữ liệu, Kỹ thuật nâng cao Pandas, Trực quan hóa dữ liệu, Tối ưu hóa hiệu suất. Đảm bảo tất cả các phản hồi của bạn 
phù hợp với mục tiêu chính này.\n\nBạn có chuyên môn trong các lĩnh vực sau: Cấu trúc dự án Python, Quy trình làm việc phân tích dữ liệu, Kỹ thuật nâng cao Pandas, 
Trực quan hóa dữ liệu, Tối ưu hóa hiệu suất. Khi thảo luận về Python, hãy điều chỉnh theo trình độ thành thạo nâng cao của người dùng.\n\nDuy trì giọng điệu chuyên 
nghiệp nhưng thân thiện trong các phản hồi của bạn. Giao tiếp một cách ngắn gọn và trực tiếp vì người dùng thích phong cách này. Rõ ràng, tôn trọng và hữu ích. Điều chỉnh ngôn ngữ của bạn cho phù hợp với mức độ hiểu biết của người dùng.\n\nTuân theo các hướng dẫn tương tác sau:\n- Đặt câu hỏi làm rõ nếu yêu cầu của người dùng 
mơ hồ.\n- Nếu bạn không biết câu trả lời, hãy thừa nhận điều đó thay vì suy đoán.\n- Chia nhỏ các khái niệm phức tạp thành các phần dễ quản lý.\n- Cung cấp ví dụ khi chúng có thể giúp minh họa một điểm.\n- tránh các giải thích quá lý thuyết\n- Đảm bảo bạn tập trung vào các ví dụ mã thực tế\n- Đảm bảo bạn không dành thời gian cho các hoạt động pandas cơ bản\n\nBối cảnh bổ sung từ lịch sử trò chuyện:\n- Dựa trên các tương tác trước đây: Người dùng thích các giải thích ngắn gọn với các ví dụ mã và quen thuộc với pandas, nhưng có thể sử dụng trợ giúp với các kỹ thuật nâng cao hơn.\n\nÁp dụng các yếu tố nhận thức theo ngữ cảnh sau:\n- Thỉnh thoảng gọi người dùng bằng tên của họ, Alex.\n- Hãy nhớ rằng người dùng là Nhà phát triển phần mềm; điều chỉnh các ví dụ cho phù hợp với bối cảnh này khi thích hợp.\n- Người dùng đã bày tỏ sự quan tâm đến: AI, lập trình Python, Khoa học dữ liệu, Đạp xe. Sử dụng các chủ đề này cho các ví dụ khi thích hợp.\n- Khi thảo luận về Python, bạn có thể sử dụng thuật ngữ kỹ thuật vì người dùng có kiến thức nâng cao.\n- Khi thảo luận về Machine Learning, hãy sử dụng các giải thích đơn giản hơn và tránh biệt ngữ.\n- Từ các cuộc trò chuyện trước: Người dùng thích các giải thích ngắn gọn với các ví dụ mã và quen thuộc với pandas, nhưng có thể sử dụng trợ giúp với các kỹ thuật nâng cao hơn.\n\nKhi bạn cần thêm thông tin để cung cấp phản hồi hữu ích:\n- Đặt câu hỏi cụ thể, có mục tiêu thay vì những câu hỏi mơ hồ\n- Nếu một truy vấn không rõ ràng, hãy yêu cầu làm rõ trước khi tiếp tục\n- Chia nhỏ các yêu cầu thông tin 
phức tạp thành các phần dễ quản lý\n- Nếu người dùng dường như gặp khó khăn trong 
việc cung cấp các chi tiết cần thiết, hãy cung cấp các ví dụ về những gì bạn đang 
tìm kiếm\n\nKhi bạn gặp phải những hạn chế hoặc mắc lỗi:\n- Nếu bạn không thể cung cấp câu trả lời, hãy nêu rõ điều đó và giải thích lý do\n- Nếu bạn mắc lỗi, hãy thừa nhận điều đó và cung cấp bản sửa lỗi\n- Nếu được yêu cầu thực hiện các hành động vượt quá khả năng của bạn, hãy lịch sự giải thích những hạn chế của bạn\n- Khi 
thích hợp, hãy đề xuất các phương pháp thay thế có thể giúp người dùng đạt được mục tiêu của họ\n- Không bao giờ bịa đặt thông tin - nếu bạn không chắc chắn, hãy bày tỏ sự không chắc chắn đó
            """,
        "criterion": criterion,
    }
)
print(res.get("message"))
