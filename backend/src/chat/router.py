import json
import logging
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as OrmSession

from src.chat.llm_client import LLMClient
from src.chat.schemas import ChatRequest
from src.chat.service import flatten_for_upstream
from src.config import Settings, get_settings
from src.database import get_db
from src.sessions import service as sess_service
from src.shared.client_id import require_client_id
from src.shared.sse import sse_text_chunk, sse_done, sse_error

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def _derive_title(messages) -> str:
    for m in messages:
        if m.role != "user":
            continue
        if isinstance(m.content, str):
            return m.content[:30]
        for p in m.content:
            ptype = p.type if hasattr(p, "type") else p.get("type")
            if ptype == "text":
                txt = p.text if hasattr(p, "text") else p.get("text", "")
                return txt[:30]
    return "新对话"


@router.post("/stream")
async def chat_stream(
    data: UploadFile = File(..., description="JSON-encoded ChatRequest"),
    file: list[UploadFile] | None = File(default=None),
    settings: Settings = Depends(get_settings),
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    try:
        raw = await data.read()
        req = ChatRequest(**json.loads(raw))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"invalid data: {e}")

    sess_service.upsert_session(db, client_id, req.sessionId, title=_derive_title(req.messages))

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if last_user is not None:
        import json as _json
        content_val = last_user.content
        if isinstance(content_val, str):
            content_str = content_val
        else:
            content_str = _json.dumps([p.dict() if hasattr(p, 'dict') else p for p in content_val], ensure_ascii=False)
        sess_service.append_message(
            db, req.sessionId, req.messageId, "user",
            content_str, "markdown",
        )

    upstream_messages = flatten_for_upstream(req.messages)
    client = LLMClient(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout_seconds,
    )

    async def gen() -> AsyncIterator[bytes]:
        started = time.monotonic()
        buf: list[str] = []
        try:
            async for piece in client.stream(upstream_messages):
                buf.append(piece)
                yield sse_text_chunk(piece).encode("utf-8")
            yield sse_done().encode("utf-8")
        except Exception as exc:
            logger.exception("upstream error")
            yield sse_error(str(exc)).encode("utf-8")
        finally:
            await client.aclose()
            elapsed_ms = int((time.monotonic() - started) * 1000)
            try:
                sess_service.append_message(
                    db, req.sessionId, req.messageId, "assistant",
                    "".join(buf), "markdown", duration_ms=elapsed_ms,
                )
            except Exception:
                logger.exception("persist assistant failed")

    return StreamingResponse(gen(), media_type="text/event-stream")
