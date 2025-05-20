from langchain_core.tools import tool
from src.utils.logger import logger


def enough_information(name: str, info: str):
    """
    Call tool nếu đã thu thập đủ thông tin cần thiết
    Args:
        name (str): Tên chatbot cần tạo
        info (str): Thông tin đã thu thập được
    """
    logger.info(f"Created successful {info}")
    return "Created successful"
