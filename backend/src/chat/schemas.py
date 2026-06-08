from typing import Literal, Union
from pydantic import BaseModel, Field


class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class FilePart(BaseModel):
    type: Literal["file"]
    file: dict  # {file_id, name, url}


class ImagePart(BaseModel):
    type: Literal["image_url"]
    image_url: dict  # {url}


ContentPart = Union[TextPart, FilePart, ImagePart]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: Union[str, list[ContentPart]]


class ChatRequest(BaseModel):
    sessionId: str
    messageId: str
    messages: list[ChatMessage] = Field(default_factory=list)
    think: bool = False
    stream: bool = True
    file_ids: list[str] = Field(default_factory=list)
    tool_id: str | None = None
    ai_ref_id: str | None = None
    module_type: str | None = None
