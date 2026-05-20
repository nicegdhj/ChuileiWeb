from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator


class Base(DeclarativeBase):
    pass


def build_engine(db_url: str) -> Engine:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    )

    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _pragmas(dbapi_conn, _):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.close()
    return engine


def get_sessionmaker(engine: Engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Module-level singletons wired by main.py at lifespan
_engine: Engine | None = None
_SessionLocal = None


def init_engine(db_url: str) -> None:
    global _engine, _SessionLocal
    _engine = build_engine(db_url)
    _SessionLocal = get_sessionmaker(_engine)


def get_engine() -> Engine:
    assert _engine is not None, "engine not initialized"
    return _engine


def get_db() -> Generator[Session, None, None]:
    assert _SessionLocal is not None, "sessionmaker not initialized"
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
