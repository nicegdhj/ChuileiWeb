import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from src.database import get_db
from src.sessions import service
from src.sessions.schemas import ApiResponse
from src.shared.client_id import require_client_id

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("")
def list_sessions(
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    rows = service.list_sessions(db, client_id)
    data = [
        {
            "sessionId": r.id,
            "title": r.title,
            "latestCreateTime": r.updated_at.isoformat(),
        }
        for r in rows
    ]
    return ApiResponse(data=data)


@router.get("/{session_id}/messages")
def get_messages(
    session_id: str,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    rows = service.get_messages(db, client_id, session_id)
    data = []
    for r in rows:
        content: object = r.content_json
        try:
            parsed = json.loads(r.content_json)
            if isinstance(parsed, list):
                content = parsed
        except (ValueError, TypeError):
            pass
        data.append({
            "messageId": r.message_id,
            "role": r.role,
            "content": content,
            "type": r.msg_type,
        })
    return ApiResponse(data=data)


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    ok = service.delete_session(db, client_id, session_id)
    return ApiResponse(code="00000" if ok else "10404", message="ok" if ok else "not found")
