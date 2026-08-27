import numpy as np
import pytest
from langchain.embeddings import Embeddings
from langchain_core.documents import Document

from versechat_backend.rag.retriever import InMemoryRetriever


class MockEmbeddings(Embeddings):
    """Mock embeddings for fast, deterministic unit testing (sync and async)."""

    def __init__(self, mapping: dict[str, list[float]]):
        self.mapping = mapping

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.mapping.get(text, [0.0, 0.0]) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.mapping.get(text, [0.0, 0.0])

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        return self.embed_query(text)


@pytest.fixture
def sample_documents() -> list[Document]:
    """Fixture providing a list of test documents."""
    return [
        Document(page_content="apples and oranges", metadata={"id": 1}),
        Document(page_content="cars and trucks", metadata={"id": 2}),
        Document(page_content="bananas and apples", metadata={"id": 3}),
    ]


@pytest.fixture
def mock_embeddings() -> MockEmbeddings:
    """Fixture providing orthogonal 2D vector mappings for easy dot-product assertions.

    - Fruit terms align with vector [1.0, 0.0]
    - Vehicle terms align with vector [0.0, 1.0]
    - Mixed terms align with vector [0.8, 0.2]
    """
    mapping = {
        "apples and oranges": [1.0, 0.0],
        "cars and trucks": [0.0, 1.0],
        "bananas and apples": [0.8, 0.2],
        "fruit query": [1.0, 0.0],
        "vehicle query": [0.0, 1.0],
    }
    return MockEmbeddings(mapping=mapping)


# ==============================================================================
# Synchronous Tests
# ==============================================================================


def test_model_post_init_creates_vectors(
    sample_documents: list[Document], mock_embeddings: MockEmbeddings
):
    """Test that _vectors private attribute is correctly initialized on instantiation."""
    retriever = InMemoryRetriever(docs=sample_documents, embeddings=mock_embeddings)

    assert hasattr(retriever, "_vectors")
    assert isinstance(retriever._vectors, np.ndarray)
    assert retriever._vectors.shape == (3, 2)
    np.testing.assert_array_almost_equal(retriever._vectors[0], np.array([1.0, 0.0]))


def test_retrieval_ranking_order(
    sample_documents: list[Document], mock_embeddings: MockEmbeddings
):
    """Test that documents are retrieved in order of dot product similarity score."""
    retriever = InMemoryRetriever(
        docs=sample_documents, embeddings=mock_embeddings, k=3
    )

    results = retriever.invoke("fruit query")

    assert len(results) == 3
    assert results[0].page_content == "apples and oranges"
    assert results[1].page_content == "bananas and apples"
    assert results[2].page_content == "cars and trucks"


def test_retrieval_respects_k_parameter(
    sample_documents: list[Document], mock_embeddings: MockEmbeddings
):
    """Test that setting k limits the number of returned documents."""
    retriever = InMemoryRetriever(
        docs=sample_documents, embeddings=mock_embeddings, k=2
    )

    results = retriever.invoke("vehicle query")

    assert len(results) == 2
    assert results[0].page_content == "cars and trucks"


def test_k_larger_than_doc_count(
    sample_documents: list[Document], mock_embeddings: MockEmbeddings
):
    """Test that retriever gracefully handles k being greater than document count."""
    retriever = InMemoryRetriever(
        docs=sample_documents, embeddings=mock_embeddings, k=10
    )

    results = retriever.invoke("fruit query")

    assert len(results) == len(sample_documents)


def test_empty_document_list(mock_embeddings: MockEmbeddings):
    """Test behavior when initialized with an empty document list."""
    retriever = InMemoryRetriever(docs=[], embeddings=mock_embeddings, k=5)

    results = retriever.invoke("any query")

    assert results == []
    assert retriever._vectors.size == 0


# ==============================================================================
# Asynchronous Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_async_retrieval_ranking_order(
    sample_documents: list[Document], mock_embeddings: MockEmbeddings
):
    """Test asynchronous retrieval via ainvoke."""
    retriever = InMemoryRetriever(
        docs=sample_documents, embeddings=mock_embeddings, k=3
    )

    results = await retriever.ainvoke("fruit query")

    assert len(results) == 3
    assert results[0].page_content == "apples and oranges"
    assert results[1].page_content == "bananas and apples"
    assert results[2].page_content == "cars and trucks"


@pytest.mark.asyncio
async def test_async_empty_document_list(mock_embeddings: MockEmbeddings):
    """Test asynchronous retrieval when initialized with an empty document list."""
    retriever = InMemoryRetriever(docs=[], embeddings=mock_embeddings, k=5)

    results = await retriever.ainvoke("any query")

    assert results == []
    assert retriever._vectors.size == 0


@pytest.mark.asyncio
async def test_afrom_documents_factory(
    sample_documents: list[Document], mock_embeddings: MockEmbeddings
):
    """Test async factory constructor initialization and retrieval."""
    retriever = await InMemoryRetriever.afrom_documents(
        docs=sample_documents,
        embeddings=mock_embeddings,
        k=2,
    )

    assert retriever._vectors.shape == (3, 2)

    results = await retriever.ainvoke("vehicle query")

    assert len(results) == 2
    assert results[0].page_content == "cars and trucks"
