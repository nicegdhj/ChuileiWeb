from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.logging_setup import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    from src.database import init_engine, Base, get_engine
    from src.sessions import models as _sm  # noqa: F401 — 注册模型
    from src.files import models as _fm  # noqa: F401
    init_engine(settings.db_url)
    Base.metadata.create_all(get_engine())
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
    from src.shared.exceptions import register_handlers
    register_handlers(app)

    health = APIRouter(prefix="/api/v1", tags=["health"])

    @health.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(health)
    from src.chat.router import router as chat_router
    app.include_router(chat_router)
    from src.sessions.router import router as sessions_router
    app.include_router(sessions_router)
    from src.files.router import router as files_router, download_router
    app.include_router(files_router)
    app.include_router(download_router)
    from src.compat.router import router as compat_router
    app.include_router(compat_router)
    return app


app = create_app()
