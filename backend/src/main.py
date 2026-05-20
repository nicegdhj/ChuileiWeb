from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.logging_setup import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="chatbox-backend", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    health = APIRouter(prefix="/api/v1", tags=["health"])

    @health.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(health)
    from src.chat.router import router as chat_router
    app.include_router(chat_router)
    return app


app = create_app()
