from fastapi import Header, HTTPException


def require_client_id(x_client_id: str = Header(default="")) -> str:
    if not x_client_id:
        raise HTTPException(status_code=400, detail="missing X-Client-Id header")
    return x_client_id
