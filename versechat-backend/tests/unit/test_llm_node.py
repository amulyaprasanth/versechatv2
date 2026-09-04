from unittest.mock import MagicMock, patch

import pytest
from langchain.messages import HumanMessage
from langchain_core.messages import SystemMessage

from versechat_backend.rag.nodes.llm_node import LLMNode, system_prompt
from versechat_backend.rag.states.state import State
from versechat_backend.rag.tools import bible_search, wiki_tool


class TestLLMNode:
    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)

        with pytest.raises(ValueError):
            LLMNode(tools=[bible_search, wiki_tool])

    @patch("versechat_backend.rag.nodes.llm_node.ChatGroq")
    def test_initialization(self, mock_chat_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "fake-key")

        _ = LLMNode(model="openai/gpt-oss-20b", tools=[bible_search, wiki_tool])

        mock_chat_groq.assert_called_once_with(model="openai/gpt-oss-20b")

    @patch("versechat_backend.rag.nodes.llm_node.ChatGroq.bind_tools")
    def test_get_node(self, mock_chat_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "fake-key")

        mock_llm = MagicMock()
        mock_response = MagicMock()

        mock_llm.invoke.return_value = mock_response
        mock_chat_groq.return_value = mock_llm

        node = LLMNode(tools=[bible_search, wiki_tool])

        state: State = {"messages": [HumanMessage(content="hello")]}

        result = node.get_node(state)
        assert result["messages"] == [mock_response]

        mock_llm.invoke.assert_called_once_with(
            [SystemMessage(content=system_prompt), HumanMessage(content="hello")]
        )
