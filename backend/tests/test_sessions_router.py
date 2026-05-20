import pytest
from fastapi.testclient import TestClient

from src.database import build_engine, get_sessionmaker, Base
from src.sessions import models  # noqa: F401
from src.sessions.service import upsert_session, append_message


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/t.sqlite"
    monkeypatch.setenv("DB_URL", db_url)
    from src.config import get_settings
    get_settings.cache_clear()

    # 先建表再启动 app
    engine = build_engine(db_url)
    Base.metadata.create_all(engine)
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as db:
        upsert_session(db, "cid-1", "sA", title="A")
        append_message(db, "sA", "m1", "user", "你好", "markdown")
        append_message(db, "sA", "m1", "assistant", "你好啊", "markdown")
        upsert_session(db, "cid-2", "sB", title="B")

    from src.main import create_app
    from src.database import init_engine
    init_engine(db_url)
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_list_sessions_filters_by_client(client):
    r = client.get("/api/v1/sessions", headers={"X-Client-Id": "cid-1"})
    assert r.status_code == 200
    data = r.json()
    assert data["code"] == "00000"
    ids = [s["sessionId"] for s in data["data"]]
    assert ids == ["sA"]


def test_get_messages(client):
    r = client.get(
        "/api/v1/sessions/sA/messages",
        headers={"X-Client-Id": "cid-1"},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert [m["role"] for m in data] == ["user", "assistant"]


def test_other_client_cannot_read(client):
    r = client.get(
        "/api/v1/sessions/sA/messages",
        headers={"X-Client-Id": "cid-2"},
    )
    assert r.status_code == 200
    assert r.json()["data"] == []


def test_delete_session(client):
    r = client.delete(
        "/api/v1/sessions/sA",
        headers={"X-Client-Id": "cid-1"},
    )
    assert r.status_code == 200
    assert r.json()["code"] == "00000"
