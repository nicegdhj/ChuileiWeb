import io
from src.files.extractor import extract_text


def test_extract_txt(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello 中文", encoding="utf-8")
    text = extract_text(str(p), "text/plain", "a.txt")
    assert "hello" in text
    assert "中文" in text


def test_extract_unsupported_returns_empty(tmp_path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"\x00\x01\x02")
    text = extract_text(str(p), "application/octet-stream", "a.bin")
    assert text == ""
