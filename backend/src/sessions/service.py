import json
from typing import Any
from sqlalchemy import select, desc
from sqlalchemy.orm import Session as OrmSession

from src.sessions.models import SessionRow, MessageRow


def upsert_session(
    db: OrmSession, client_id: str, session_id: str, *, title: str | None = None
) -> SessionRow:
    row = db.get(SessionRow, session_id)
    if row is None:
        row = SessionRow(id=session_id, client_id=client_id, title=title or "新对话")
        db.add(row)
    elif title and row.title in ("新对话", ""):
        row.title = title
    db.commit()
    db.refresh(row)
    return row


def list_sessions(db: OrmSession, client_id: str, limit: int = 50) -> list[SessionRow]:
    stmt = (
        select(SessionRow)
        .where(SessionRow.client_id == client_id)
        .order_by(desc(SessionRow.updated_at))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars())


def append_message(
    db: OrmSession,
    session_id: str,
    message_id: str,
    role: str,
    content: str | list[Any],
    msg_type: str,
    duration_ms: int = 0,
) -> MessageRow:
    payload = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    row = MessageRow(
        session_id=session_id,
        message_id=message_id,
        role=role,
        content_json=payload,
        msg_type=msg_type,
        duration_ms=duration_ms,
    )
    db.add(row)
    sess = db.get(SessionRow, session_id)
    if sess:
        from datetime import datetime, timezone
        sess.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def get_messages(db: OrmSession, client_id: str, session_id: str) -> list[MessageRow]:
    sess = db.get(SessionRow, session_id)
    if sess is None or sess.client_id != client_id:
        return []
    return list(sess.messages)


def delete_session(db: OrmSession, client_id: str, session_id: str) -> bool:
    sess = db.get(SessionRow, session_id)
    if sess is None or sess.client_id != client_id:
        return False
    db.delete(sess)
    db.commit()
    return True
