from unittest.mock import patch

import pytest
from langchain.embeddings import Embeddings
from langchain_core.documents import Document


class MockEmbeddings(Embeddings):
    """Deterministic mock embeddings for fast unit testing."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        return self.embed_query(text)


@pytest.fixture
def mock_wiki_retriever():
    """Fixture that initializes WikiRetriever with mocked HuggingFaceEmbeddings."""
    with patch(
        "versechat_backend.rag.wiki_retriever.HuggingFaceEmbeddings",
        return_value=MockEmbeddings(),
    ):
        from versechat_backend.rag.wiki_retriever import WikiRetriever

        retriever = WikiRetriever(default_k=3)
        yield retriever


# ==============================================================================
# Synchronous Tests
# ==============================================================================


@patch("versechat_backend.rag.wiki_retriever.wikipedia_search")
def test_invoke_success(mock_wiki, mock_wiki_retriever):
    """Test successful synchronous retrieval from a Wikipedia topic."""
    mock_wiki.return_value = (
        "Jerusalem is a city in West Asia. It is one of the oldest cities in the world."
    )

    results = mock_wiki_retriever.invoke(query="oldest cities", topic="jerusalem")

    mock_wiki.assert_called_once_with("jerusalem")
    assert len(results) > 0
    assert isinstance(results[0], Document)
    assert "Jerusalem" in results[0].page_content


@patch("versechat_backend.rag.wiki_retriever.wikipedia_search")
def test_invoke_empty_content(mock_wiki, mock_wiki_retriever):
    """Test behavior when Wikipedia tool returns empty content."""
    mock_wiki.return_value = "   "

    results = mock_wiki_retriever.invoke(query="any query", topic="non_existent_topic")

    mock_wiki.assert_called_once_with("non_existent_topic")
    assert results == []


# ==============================================================================
# Asynchronous Tests
# ==============================================================================


@pytest.mark.asyncio
@patch("versechat_backend.rag.wiki_retriever.wikipedia_search")
async def test_ainvoke_success(mock_wiki, mock_wiki_retriever):
    """Test successful asynchronous retrieval using ainvoke."""
    mock_wiki.return_value = "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics."

    results = await mock_wiki_retriever.ainvoke(
        query="what is quantum computing", topic="quantum computing"
    )

    mock_wiki.assert_called_once_with("quantum computing")
    assert len(results) > 0
    assert isinstance(results[0], Document)
    assert "Quantum computing" in results[0].page_content


@pytest.mark.asyncio
@patch("versechat_backend.rag.wiki_retriever.wikipedia_search")
async def test_ainvoke_empty_content(mock_wiki, mock_wiki_retriever):
    """Test async behavior when Wikipedia tool returns empty string/None."""
    mock_wiki.return_value = ""

    results = await mock_wiki_retriever.ainvoke(query="any query", topic="empty_topic")

    mock_wiki.assert_called_once_with("empty_topic")
    assert results == []
