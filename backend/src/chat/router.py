import json
import logging
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as OrmSession

from src.chat.llm_client import LLMClient
from src.chat.schemas import ChatRequest
from src.chat.service import flatten_for_upstream
from src.config import Settings, get_settings
from src.database import get_db
from src.files import service as files_service
from src.sessions import service as sess_service
from src.shared.client_id import require_client_id
from src.shared.sse import sse_text_chunk, sse_done, sse_error
from src.files.models import FileRow
from src.chat.xinling_bridge import (
    upload_pcap_file,
    fetch_pcap_msg,
    get_pcap_modules,
    run_xinling_swimlane_bridge,
)

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


def _run_chat_stream(
    req: ChatRequest,
    client_id: str,
    db: OrmSession,
    settings: Settings,
) -> StreamingResponse:
    """核心流式逻辑：写入用户消息 → 调 LLM → SSE 输出 → 写入 assistant 消息。"""
    # 情况 A: 点击了绘制信令泳道图按钮
    if req.tool_id == "import_pcap_by_id":
        sess_service.append_message(
            db, req.sessionId, req.messageId, "user",
            "点击绘制信令泳道图", "markdown"
        )
        
        async def gen() -> AsyncIterator[bytes]:
            reports_json = "[]"
            try:
                async for piece in run_xinling_swimlane_bridge(
                    api_base_url=settings.xinling_api_base_url,
                    ai_ref_id=req.ai_ref_id,
                ):
                    reports_json = piece
                    # 推送类型为 "xinling" 的 SSE 帧，前端会自动弹窗绘制泳道图
                    yield sse_text_chunk(piece, "xinling").encode("utf-8")
                
                # 持久化该条泳道图消息
                sess_service.append_message(
                    db, req.sessionId, f"{req.messageId}_chart", "assistant",
                    reports_json, "xinling"
                )
                yield sse_done().encode("utf-8")
            except Exception as exc:
                logger.exception("xinling swimlane error")
                yield sse_error(str(exc)).encode("utf-8")
        
        return StreamingResponse(gen(), media_type="text/event-stream")

    # 情况 B: 点击了特定模块的根因推理按钮
    if req.tool_id == "get_pcap_msg":
        sess_service.append_message(
            db, req.sessionId, req.messageId, "user",
            f"开始进行【{req.module_type or '未知模块'}】推理", "markdown"
        )
        
        async def gen() -> AsyncIterator[bytes]:
            started = time.monotonic()
            buf: list[str] = []
            try:
                async for piece in fetch_pcap_msg(
                    api_base_url=settings.xinling_api_base_url,
                    ai_ref_id=req.ai_ref_id,
                    module_type=req.module_type or "综合分析",
                ):
                    buf.append(piece)
                    yield sse_text_chunk(piece).encode("utf-8")
                yield sse_done().encode("utf-8")
            except Exception as exc:
                logger.exception("xinling module msg error")
                yield sse_error(str(exc)).encode("utf-8")
            finally:
                elapsed_ms = int((time.monotonic() - started) * 1000)
                try:
                    sess_service.append_message(
                        db, req.sessionId, f"{req.messageId}_reason", "assistant",
                        "".join(buf), "markdown", duration_ms=elapsed_ms,
                    )
                except Exception:
                    logger.exception("persist assistant failed")
        
        return StreamingResponse(gen(), media_type="text/event-stream")

    # 情况 C: 新上传了信令 pcap/pcapng 文件
    pcap_file = None
    if req.file_ids:
        pcap_file = db.query(FileRow).filter(
            FileRow.id.in_(req.file_ids)
        ).filter(
            (FileRow.original_name.like("%.pcap")) | (FileRow.original_name.like("%.pcapng"))
        ).first()

    # 依然先把会话标题和用户消息落库
    sess_service.upsert_session(db, client_id, req.sessionId, title=_derive_title(req.messages))

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if last_user is not None:
        content_val = last_user.content
        if isinstance(content_val, str):
            content_str = content_val
        else:
            content_str = json.dumps(
                [p.dict() if hasattr(p, 'dict') else p for p in content_val],
                ensure_ascii=False,
            )
        sess_service.append_message(
            db, req.sessionId, req.messageId, "user",
            content_str, "markdown",
        )

    # 如果是信令文件，直接重定向到信令分析桥接流，分析结束后下发卡片按钮
    if pcap_file is not None:
        pcap_name = pcap_file.original_name
        pcap_path = pcap_file.stored_path

        async def gen() -> AsyncIterator[bytes]:
            started = time.monotonic()
            buf: list[str] = []
            try:
                yield sse_text_chunk("正在上传并解析信令抓包文件，请稍候...\n\n").encode("utf-8")
                
                # 1. 异步上传
                ai_ref_id = await upload_pcap_file(
                    api_base_url=settings.xinling_api_base_url,
                    file_name=pcap_name,
                    file_path=pcap_path,
                )
                
                # 2. 流式获取综合分析
                async for piece in fetch_pcap_msg(
                    api_base_url=settings.xinling_api_base_url,
                    ai_ref_id=ai_ref_id,
                    module_type="综合分析",
                ):
                    buf.append(piece)
                    yield sse_text_chunk(piece).encode("utf-8")
                
                # 综合分析文本落库
                elapsed_ms = int((time.monotonic() - started) * 1000)
                sess_service.append_message(
                    db, req.sessionId, req.messageId, "assistant",
                    "".join(buf), "markdown", duration_ms=elapsed_ms,
                )
                
                # 3. 综合分析结束后，拉取可用模块拼装卡片按钮
                modules = await get_pcap_modules(settings.xinling_api_base_url, ai_ref_id)
                options = []
                # 选项 1: 绘制信令泳道图
                options.append({
                    "title": "点击绘制信令泳道图",
                    "selected": 0,
                    "action": 1,
                    "showQuestion": 0,
                    "dataParams": {
                        "tool_id": "import_pcap_by_id",
                        "ai_ref_id": ai_ref_id,
                    }
                })
                # 选项 2: 推理诊断
                if modules:
                    target_mod = modules[-1]
                    options.append({
                        "title": target_mod.get("display", "根因推理"),
                        "selected": 1,
                        "action": 1,
                        "showQuestion": 0,
                        "dataParams": {
                            "tool_id": "get_pcap_msg",
                            "ai_ref_id": ai_ref_id,
                            "module_type": target_mod.get("value", "")
                        }
                    })
                
                card_data = {
                    "content": "",
                    "options": options
                }
                card_json_str = json.dumps(card_data, ensure_ascii=False)
                
                # 吐出 cardBtn 给前端
                yield sse_text_chunk(card_json_str, "cardBtn").encode("utf-8")
                
                # 将卡片按钮独立作为一条消息落库
                sess_service.append_message(
                    db, req.sessionId, f"{req.messageId}_btn", "assistant",
                    card_json_str, "cardBtn"
                )
                
                yield sse_done().encode("utf-8")
            except Exception as exc:
                logger.exception("xinling upload and analyze error")
                yield sse_error(str(exc)).encode("utf-8")
                try:
                    sess_service.append_message(
                        db, req.sessionId, req.messageId, "assistant",
                        f"解析失败: {str(exc)}", "markdown"
                    )
                except Exception:
                    pass
        
        return StreamingResponse(gen(), media_type="text/event-stream")

    # 4. 原有的普通 LLM 问答逻辑
    file_texts = files_service.texts_for(db, req.file_ids)
    upstream_messages = flatten_for_upstream(req.messages, file_texts=file_texts)
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
            async for piece in client.stream(upstream_messages, think=req.think):
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


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    settings: Settings = Depends(get_settings),
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    """SSE 流式对话。

    请求体：标准 JSON（ChatRequest）
    响应：text/event-stream，每帧形如 `data: {"code":"00000","choices":[...]}`

    带文件时：先 POST /files 上传，把返回的 file_id 放进 ChatRequest.file_ids。
    """
    return _run_chat_stream(req, client_id, db, settings)
