import os
import uuid
from sqlalchemy.orm import Session as OrmSession

from src.config import get_settings
from src.files.extractor import extract_text
from src.files.models import FileRow


async def save_upload(db: OrmSession, *, client_id: str, session_id: str | None,
                      filename: str, content: bytes, mime: str) -> FileRow:
    settings = get_settings()
    file_id = uuid.uuid4().hex
    subdir = session_id or "_loose"
    base_dir = os.path.abspath(settings.upload_dir)
    target_dir = os.path.join(base_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)
    safe_name = filename.replace("/", "_").replace("\\", "_")
    stored = os.path.join(target_dir, f"{file_id}_{safe_name}")
    with open(stored, "wb") as f:
        f.write(content)
    text = extract_text(stored, mime, safe_name)
    row = FileRow(
        id=file_id, client_id=client_id, session_id=session_id,
        original_name=safe_name, stored_path=stored, mime=mime, size=len(content),
        extracted_text=text,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_file(db: OrmSession, client_id: str, file_id: str) -> FileRow | None:
    row = db.get(FileRow, file_id)
    if row is None or row.client_id != client_id:
        return None
    return row


def texts_for(db: OrmSession, file_ids: list[str]) -> dict[str, str]:
    if not file_ids:
        return {}
    rows = db.query(FileRow).filter(FileRow.id.in_(file_ids)).all()
    return {r.id: r.extracted_text or "" for r in rows}
