from sqlalchemy import text
from src.database import build_engine, get_sessionmaker


def test_engine_executes_wal_pragma(tmp_path):
    db_path = tmp_path / "x.sqlite"
    engine = build_engine(f"sqlite:///{db_path}")
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as s:
        mode = s.execute(text("PRAGMA journal_mode")).scalar()
    assert str(mode).lower() == "wal"
