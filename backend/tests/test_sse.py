import json
from src.shared.sse import sse_text_chunk, sse_done


def test_sse_text_chunk_format():
    line = sse_text_chunk("hello")
    assert line.startswith("data: ")
    assert line.endswith("\n\n")
    payload = json.loads(line[len("data: "):].strip())
    assert payload["code"] == "00000"
    assert payload["choices"][0]["type"] == "markdown"
    assert payload["choices"][0]["message"]["content"] == "hello"


def test_sse_done_frame():
    line = sse_done()
    payload = json.loads(line[len("data: "):].strip())
    assert payload["choices"][0]["finish_reason"] == "stop"
