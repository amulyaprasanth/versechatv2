from contextlib import asynccontextmanager
from importlib import import_module

import pytest


@pytest.mark.asyncio
async def test_app_does_not_start_when_agent_initialization_fails(monkeypatch):
    app_module = import_module("versechat_backend.app")

    class FakeCheckpointer:
        async def setup(self):
            return None

    @asynccontextmanager
    async def fake_saver_context(*_args, **_kwargs):
        yield FakeCheckpointer()

    def fail_graph_builder(_checkpointer):
        raise ValueError("graph initialization failed")

    monkeypatch.setattr(app_module.Base.metadata, "create_all", lambda **_kwargs: None)
    monkeypatch.setattr(
        app_module.AsyncPostgresSaver,
        "from_conn_string",
        staticmethod(lambda *_args, **_kwargs: fake_saver_context()),
    )
    monkeypatch.setattr(app_module, "GraphBuilder", fail_graph_builder)

    with pytest.raises(ValueError, match="graph initialization failed"):
        async with app_module.lifespan(app_module.app):
            pass
