from src.chat.schemas import ChatMessage


def flatten_for_upstream(
    messages: list[ChatMessage],
    *,
    file_texts: dict[str, str] | None = None,
) -> list[dict]:
    """把多模态 parts 数组扁平化为上游模型期望的纯文本 content。"""
    file_texts = file_texts or {}
    flat: list[dict] = []
    for m in messages:
        if isinstance(m.content, str):
            flat.append({"role": m.role, "content": m.content})
            continue
        text_buf: list[str] = []
        for part in m.content:
            ptype = part.type if hasattr(part, "type") else part.get("type")
            if ptype == "text":
                text_buf.append(part.text if hasattr(part, "text") else part.get("text", ""))
            elif ptype == "file":
                fobj = part.file if hasattr(part, "file") else part.get("file", {})
                name = fobj.get("name", "attachment")
                fid = fobj.get("file_id", "")
                extra = file_texts.get(fid, "")
                if extra:
                    text_buf.append(f"\n\n---\n附件「{name}」内容：\n{extra}")
                else:
                    text_buf.append(f"\n\n[附件：{name}]")
            elif ptype == "image_url":
                text_buf.append("\n\n[图片附件，当前模型暂不支持图像理解]")
        flat.append({"role": m.role, "content": "".join(text_buf).strip()})
    return flat
