import pytest
from sqlalchemy.orm import Session as OrmSession

from src.database import build_engine, get_sessionmaker, Base
from src.sessions import models  # noqa: F401
from src.sessions.service import (
    upsert_session, list_sessions, append_message, get_messages, delete_session,
)


@pytest.fixture()
def db(tmp_path) -> OrmSession:
    engine = build_engine(f"sqlite:///{tmp_path}/t.sqlite")
    Base.metadata.create_all(engine)
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as s:
        yield s


def test_upsert_and_list(db):
    upsert_session(db, "cid", "s1", title="hello")
    upsert_session(db, "cid", "s2", title="world")
    rows = list_sessions(db, "cid")
    assert {r.id for r in rows} == {"s1", "s2"}
    rows_other = list_sessions(db, "other")
    assert rows_other == []


def test_append_and_fetch_messages(db):
    upsert_session(db, "cid", "s1")
    append_message(db, "s1", "m1", "user", "你好", "markdown")
    append_message(db, "s1", "m1", "assistant", "你好啊", "markdown")
    rows = get_messages(db, "cid", "s1")
    assert [r.role for r in rows] == ["user", "assistant"]


def test_delete_session_cascades(db):
    upsert_session(db, "cid", "s1")
    append_message(db, "s1", "m1", "user", "x", "markdown")
    delete_session(db, "cid", "s1")
    assert get_messages(db, "cid", "s1") == []
