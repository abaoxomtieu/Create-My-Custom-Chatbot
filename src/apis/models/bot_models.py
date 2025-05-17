from pydantic import Field
from typing import Literal
from .BaseDocument import BaseDocument
from bson import ObjectId

class Bot(BaseDocument):
    id: ObjectId = Field("", description="ID of the bot")
    name: str = Field(default="", description="Name of the bot")
    prompt: str = Field(default="", description="Prompt of the bot")
    tools: list = Field(default=[], description="Tools of the bot")

    