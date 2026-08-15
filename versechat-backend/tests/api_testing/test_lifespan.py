import sys
import types

import pytest
from fastapi.testclient import TestClient

from versechat_backend.app import app


class FailingBibleAgent:
    def __init__(self, *args, **kwargs):
        raise ValueError("GROQ_API_KEY is missing")


def test_app_does_not_start_when_agent_initialization_fails(monkeypatch):
    fake_tools_module = types.ModuleType("versechat_backend.rag.tools")
    fake_tools_module.bible_search = object()
    fake_tools_module.wiki_tool = object()

    fake_agent_module = types.ModuleType("versechat_backend.rag.bible_agent")
    fake_agent_module.BibleAgent = FailingBibleAgent

    monkeypatch.setitem(sys.modules, "versechat_backend.rag.tools", fake_tools_module)
    monkeypatch.setitem(
        sys.modules,
        "versechat_backend.rag.bible_agent",
        fake_agent_module,
    )

    with pytest.raises(ValueError, match="GROQ_API_KEY is missing"), TestClient(app):
        pass
