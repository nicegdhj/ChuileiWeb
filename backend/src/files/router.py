import os
import mimetypes
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as OrmSession

from src.database import get_db
from src.files import service
from src.shared.client_id import require_client_id

router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.post("")
async def upload(
    file: UploadFile = File(...),
    sessionId: str | None = None,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    content = await file.read()
    mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    row = await service.save_upload(
        db, client_id=client_id, session_id=sessionId,
        filename=file.filename or "file.bin",
        content=content, mime=mime,
    )
    return {
        "code": "00000",
        "data": {
            "file_id": row.id,
            "name": row.original_name,
            "url": f"/files/{row.id}",
            "mime": row.mime, "size": row.size,
        },
    }


download_router = APIRouter(tags=["files"])


@download_router.get("/files/{file_id}")
def download(
    file_id: str,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    row = service.get_file(db, client_id, file_id)
    if row is None or not os.path.exists(row.stored_path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(row.stored_path, media_type=row.mime, filename=row.original_name)
