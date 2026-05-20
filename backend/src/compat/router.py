from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy import select

from src.database import get_db
from src.sessions.models import MessageRow

router = APIRouter(prefix="/api/v1", tags=["compat"])


@router.post("/scene/use")
async def scene_use() -> dict:
    return {"code": "00000", "data": []}


@router.get("/chat/duration/{message_id}")
async def chat_duration(message_id: str, db: OrmSession = Depends(get_db)) -> dict:
    stmt = (
        select(MessageRow.duration_ms)
        .where(MessageRow.message_id == message_id, MessageRow.role == "assistant")
        .order_by(MessageRow.id.desc())
        .limit(1)
    )
    val = db.execute(stmt).scalar()
    return {"code": "00000", "data": int(val) if val else 0}
