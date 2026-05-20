import json
import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from src.main import create_app


def test_chat_stream_basic(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen3-32b")
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
        client = TestClient(create_app())
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
            files={"data": ("data.json", json.dumps(payload), "application/json")},
            headers={"X-Client-Id": "test-client"},
        ) as resp:
            assert resp.status_code == 200
            chunks = list(resp.iter_lines())
    joined = "\n".join(chunks)
    assert "你好" in joined
    assert "finish_reason" in joined
