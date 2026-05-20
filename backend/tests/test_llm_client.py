import httpx
import pytest
import respx

from src.chat.llm_client import LLMClient


@pytest.mark.asyncio
async def test_stream_yields_delta_contents():
    base = "http://fake-llm/v1"
    body = (
        'data: {"choices":[{"delta":{"content":"你好"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"，世界"}}]}\n\n'
        'data: [DONE]\n\n'
    )
    with respx.mock(assert_all_called=True) as r:
        r.post(f"{base}/chat/completions").mock(
            return_value=httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})
        )
        client = LLMClient(base_url=base, model="qwen3-32b", api_key="", max_tokens=128, timeout=30)
        out: list[str] = []
        async for chunk in client.stream([{"role": "user", "content": "hi"}]):
            out.append(chunk)
        await client.aclose()
    assert "".join(out) == "你好，世界"
