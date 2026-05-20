from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SessionSummary(BaseModel):
    sessionId: str
    title: str
    latestCreateTime: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    messageId: str
    role: str
    content: str | list[dict]
    type: str
    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel):
    code: str = "00000"
    message: str = "ok"
    data: object | None = None
