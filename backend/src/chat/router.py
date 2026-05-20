import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from src.chat.llm_client import LLMClient
from src.chat.schemas import ChatRequest
from src.chat.service import flatten_for_upstream
from src.config import Settings, get_settings
from src.shared.sse import sse_text_chunk, sse_done, sse_error

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    data: UploadFile = File(..., description="JSON-encoded ChatRequest"),
    file: list[UploadFile] | None = File(default=None),
    settings: Settings = Depends(get_settings),
):
    try:
        raw = await data.read()
        req = ChatRequest(**json.loads(raw))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"invalid data: {e}")

    upstream_messages = flatten_for_upstream(req.messages)
    client = LLMClient(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout_seconds,
    )

    async def gen() -> AsyncIterator[bytes]:
        try:
            async for piece in client.stream(upstream_messages):
                yield sse_text_chunk(piece).encode("utf-8")
            yield sse_done().encode("utf-8")
        except Exception as exc:
            logger.exception("upstream error")
            yield sse_error(str(exc)).encode("utf-8")
        finally:
            await client.aclose()

    return StreamingResponse(gen(), media_type="text/event-stream")
