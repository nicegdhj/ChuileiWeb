import json
import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from src.main import create_app


def test_chat_stream_basic(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen3-32b")
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path}/basic.sqlite")
    from src.config import get_settings
    get_settings.cache_clear()

    body = (
        'data: {"choices":[{"delta":{"content":"你好"}}]}\n\n'
        'data: [DONE]\n\n'
    )
    with respx.mock() as r:
        r.post("http://fake-llm/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=body)
        )
        with TestClient(create_app()) as client:
            payload = {
                "sessionId": "s1",
                "messageId": "m1",
                "messages": [{"role": "user", "content": "hi"}],
                "think": False,
                "stream": True,
            }
            with client.stream(
                "POST",
                "/api/v1/chat/stream",
                json=payload,
                headers={"X-Client-Id": "test-client"},
            ) as resp:
                assert resp.status_code == 200
                chunks = list(resp.iter_lines())
    joined = "\n".join(chunks)
    assert "你好" in joined
    assert "finish_reason" in joined


def test_chat_stream_persists_messages(monkeypatch, tmp_path):
    db_url = f"sqlite:///{tmp_path}/t.sqlite"
    monkeypatch.setenv("DB_URL", db_url)
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    from src.config import get_settings
    get_settings.cache_clear()

    body = (
        'data: {"choices":[{"delta":{"content":"hi"}}]}\n\n'
        'data: [DONE]\n\n'
    )
    import httpx, respx, json
    from fastapi.testclient import TestClient
    from src.main import create_app
    from src.database import build_engine, get_sessionmaker, Base
    from src.sessions import models  # noqa: F401
    from src.sessions.service import get_messages, upsert_session

    with respx.mock() as r:
        r.post("http://fake-llm/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=body)
        )
        with TestClient(create_app()) as client:
            payload = {
                "sessionId": "ss1",
                "messageId": "mm1",
                "messages": [{"role": "user", "content": "你好"}],
                "think": False, "stream": True,
            }
            with client.stream(
                "POST", "/api/v1/chat/stream",
                json=payload,
                headers={"X-Client-Id": "cidX"},
            ) as resp:
                list(resp.iter_lines())

    engine = build_engine(db_url)
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as db:
        rows = get_messages(db, "cidX", "ss1")
    roles = [r.role for r in rows]
    assert roles == ["user", "assistant"]
    assert "hi" in rows[1].content_json


def test_chat_stream_injects_file_text(monkeypatch, tmp_path):
    db_url = f"sqlite:///{tmp_path}/t.sqlite"
    monkeypatch.setenv("DB_URL", db_url)
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "up"))
    from src.config import get_settings
    get_settings.cache_clear()

    import httpx, respx, json
    from fastapi.testclient import TestClient
    from src.main import create_app

    captured_body = {}

    def _capture(request: httpx.Request):
        captured_body["payload"] = json.loads(request.content)
        body = 'data: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n'
        return httpx.Response(200, text=body)

    with respx.mock() as r:
        r.post("http://fake-llm/v1/chat/completions").mock(side_effect=_capture)
        with TestClient(create_app()) as client:
            # 先上传一个文件
            up = client.post(
                "/api/v1/files",
                headers={"X-Client-Id": "cidF"},
                files={"file": ("note.txt", "重要语料 abc", "text/plain")},
            )
            file_id = up.json()["data"]["file_id"]
            # 发起会话，附带 file_id
            payload = {
                "sessionId": "ssf", "messageId": "mmf",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请总结附件"},
                        {"type": "file", "file": {"file_id": file_id, "name": "note.txt", "url": f"/files/{file_id}"}},
                    ],
                }],
                "file_ids": [file_id],
                "think": False, "stream": True,
            }
            with client.stream(
                "POST", "/api/v1/chat/stream",
                json=payload,
                headers={"X-Client-Id": "cidF"},
            ) as resp:
                list(resp.iter_lines())

    upstream_content = captured_body["payload"]["messages"][0]["content"]
    assert "重要语料 abc" in upstream_content
    assert "note.txt" in upstream_content
