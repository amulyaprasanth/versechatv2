from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from versechat_backend import utils
from versechat_backend.app import app
from versechat_backend.database import Base, get_db


class FakeAgent:
    async def ainvoke(self, *args, **kwargs):
        return {"messages": [SimpleNamespace(content="Test answer")]}

    async def aget_state(self, *args, **kwargs):
        return SimpleNamespace(values={"messages": []})

    async def astream(self, *args, **kwargs):
        yield {
            "type": "messages",
            "data": (SimpleNamespace(content="Test answer"), {"langgraph_node": "llm"}),
        }


class FakeCheckpointer:
    def __init__(self):
        self.adelete_thread = AsyncMock()


@pytest.fixture
def client(monkeypatch):
    # Use an isolated in-memory database and a fake graph/checkpointer. These
    # tests must never connect to the developer's or production PostgreSQL DB.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=True)
    monkeypatch.setattr(utils, "hash_password", lambda _password: "test-hash")
    monkeypatch.setattr(
        utils,
        "verify_password",
        lambda password, hashed: (
            hashed == "test-hash" and password == "SecurePassword123!"
        ),
    )

    def override_get_db():
        with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    checkpointer = FakeCheckpointer()

    @asynccontextmanager
    async def test_lifespan(_app):
        _app.state.checkpointer = checkpointer
        _app.state.agent = FakeAgent()
        yield

    monkeypatch.setattr(app.router, "lifespan_context", test_lifespan)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()
