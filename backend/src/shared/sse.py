import json
from typing import Any


def _frame(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def sse_text_chunk(content: str, msg_type: str = "markdown") -> str:
    return _frame({
        "code": "00000",
        "choices": [{
            "type": msg_type,
            "message": {"content": content},
        }],
    })


def sse_done() -> str:
    return _frame({
        "code": "00000",
        "choices": [{"finish_reason": "stop"}],
    })


def sse_error(message: str, code: str = "10000") -> str:
    return _frame({"code": code, "message": message, "choices": []})
