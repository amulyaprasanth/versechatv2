import asyncio
import os
from collections import defaultdict

import bm25s
from langchain_core.documents import Document

from versechat_backend.core.logger import get_logger
from versechat_backend.rag.bm25_search import BM25Retriever
from versechat_backend.rag.vectorstore import VectorStore
from versechat_backend.utils import convert_bible_documents

logger = get_logger()

SEMANTIC_K = os.getenv("SEMANTIC_K", "10")
KEYWORD_K = os.getenv("KEYWORD_K", "10")
FINAL_K = os.getenv("FINAL_K", "8")


class HybridSearch:
    def __init__(self):

        self.bm25 = BM25Retriever()
        self.vectorstore = VectorStore()
        self.bm25_retriever = None
        self.ids: list[str] = []

    @classmethod
    async def create(cls):
        instance = cls()
        await instance.setup_search()
        return instance

    async def setup_search(self):
        docs, self.ids = await convert_bible_documents("./bible/books")

        existing_docs = await self.vectorstore.store.asimilarity_search(
            query="Bible",
            k=1,
        )

        if not existing_docs:
            logger.info("Vector store is empty. Adding documents.")
            await self.vectorstore.setup_store(docs, self.ids)
        else:
            logger.info("Vector store already contains documents. Skipping indexing.")

        self.bm25_retriever = self.bm25.create_retriever(docs)

    async def asemantic_search(
        self,
        query: str,
        k: int = int(SEMANTIC_K),
    ) -> list[Document]:
        """Perform asynchronous semantic similarity search against PGVector.

        Args:
            query: Natural language query used to retrieve relevant verses.
            k: Maximum number of documents to retrieve.

        Returns:
            A list of the most semantically relevant Bible documents.
        """
        return await self.vectorstore.store.asimilarity_search(query, k)

    def keyword_search(self, query: str, k: int = int(KEYWORD_K)) -> list[dict]:
        """Performs key word search aginst the bm25 index"""
        tokenized_query = bm25s.tokenize(
            [query], stopwords=self.bm25.corpus_lang, stemmer=self.bm25.stemmer
        )
        results = self.bm25_retriever.retrieve(tokenized_query, k=k)  # type:ignore

        indices = results.documents[0]  # type:ignore
        scores = results.scores[0]  # type:ignore

        return [
            {
                "id": self.ids[int(index)],
                "score": float(score),
            }
            for index, score in zip(indices, scores)
            if index >= 0
        ]

    async def ahybrid_search(self, query: str, top_k: int = int(FINAL_K), k: int = 60):
        semantic_results, keyword_results = await asyncio.gather(
            self.asemantic_search(query),
            asyncio.to_thread(self.keyword_search, query),
        )

        semantic_ids = [doc.id for doc in semantic_results]
        keyword_ids = [doc["id"] for doc in keyword_results]

        rrf_scores: dict[str, float] = defaultdict(float)
        for ids in [semantic_ids, keyword_ids]:
            for rank, id in enumerate(ids, start=1):
                rrf_scores[id] += 1.0 / (k + rank)

        ranked_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        top_k_docs = [doc_id for doc_id, score in ranked_results[:top_k]]

        docs = await self.vectorstore.store.aget_by_ids(top_k_docs)

        return docs


async def main():
    hybridsearch = await HybridSearch.create()

    query = "god is love"
    results = await hybridsearch.ahybrid_search(query)

    print(results)


if __name__ == "__main__":
    asyncio.run(main())
