import pytest

from src.chat.service import flatten_for_upstream
from src.chat.schemas import ChatMessage


def test_flatten_string_content():
    out = flatten_for_upstream([
        ChatMessage(role="user", content="你好"),
        ChatMessage(role="assistant", content="你好啊"),
    ])
    assert out == [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好啊"},
    ]


def test_flatten_multimodal_text_only():
    msg = ChatMessage(role="user", content=[
        {"type": "text", "text": "总结一下"},
        {"type": "file", "file": {"file_id": "f1", "name": "a.txt", "url": "/files/f1"}},
    ])
    out = flatten_for_upstream([msg], file_texts={"f1": "这是文件内容"})
    assert out[0]["role"] == "user"
    assert "总结一下" in out[0]["content"]
    assert "这是文件内容" in out[0]["content"]
    assert "a.txt" in out[0]["content"]
