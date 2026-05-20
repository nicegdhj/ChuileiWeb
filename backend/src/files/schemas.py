from pydantic import BaseModel


class FileMeta(BaseModel):
    file_id: str
    name: str
    url: str
    mime: str
    size: int
