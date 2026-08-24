import sys
import types

import pytest
from fastapi.testclient import TestClient

from versechat_backend.app import app


class FakeBibleAgent:
    def __init__(self, *args, **kwargs):
        pass

    async def ask(self, query: str):
        return (
            "Moses led Israel out of Egypt.",
            [
                {
                    "tool_name": "bible_search",
                    "tool_output": "Exodus 20:5",
                }
            ],
        )


@pytest.fixture
def client(monkeypatch):
    fake_tools_module = types.ModuleType("versechat_backend.rag.tools")
    fake_tools_module.bible_search = object()
    fake_tools_module.wiki_tool = object()

    fake_agent_module = types.ModuleType("versechat_backend.rag.bible_agent")
    fake_agent_module.BibleAgent = FakeBibleAgent

    monkeypatch.setitem(
        sys.modules,
        "versechat_backend.rag.tools",
        fake_tools_module,
    )
    monkeypatch.setitem(
        sys.modules,
        "versechat_backend.rag.bible_agent",
        fake_agent_module,
    )

    with TestClient(app) as test_client:
        yield test_client
