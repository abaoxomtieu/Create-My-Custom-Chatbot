import logging
import os
from datetime import datetime
from pathlib import Path

import pytz
from loguru import logger


class CoreCFG:
    PROJECT_NAME = "Robokki"
    BOT_NAME = str("Robokki")


def get_date_time():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))




logger = logger
