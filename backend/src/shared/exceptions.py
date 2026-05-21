from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, detail: str):
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exc(_req: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.error_code, "message": exc.detail, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def _val_exc(_req: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"code": "VALIDATION_ERROR", "message": str(exc.errors()), "data": None},
        )
