from typing import Self

import numpy as np
from langchain.embeddings import Embeddings
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import PrivateAttr


class InMemoryRetriever(BaseRetriever):
    docs: list[Document]
    embeddings: Embeddings
    k: int = 5

    _vectors: np.ndarray = PrivateAttr()

    def model_post_init(self, __context, /) -> None:
        if self.docs:
            self._vectors = np.array(
                self.embeddings.embed_documents([doc.page_content for doc in self.docs])
            )
        else:
            self._vectors = np.empty((0, 0))

    # --- Synchronous Retrieval ---
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        if not self.docs or self._vectors.size == 0:
            return []

        query_vector = np.array(self.embeddings.embed_query(query))
        scores = self._vectors @ query_vector
        top_indices = np.argsort(scores)[::-1][: self.k]

        return [self.docs[i] for i in top_indices]

    # --- Asynchronous Retrieval ---
    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
    ) -> list[Document]:
        if not self.docs or self._vectors.size == 0:
            return []

        # Await async query embedding
        query_vector = np.array(await self.embeddings.aembed_query(query))

        scores = self._vectors @ query_vector
        top_indices = np.argsort(scores)[::-1][: self.k]

        return [self.docs[i] for i in top_indices]

    # --- Async Factory Constructor (Optional) ---
    @classmethod
    async def afrom_documents(
        cls,
        docs: list[Document],
        embeddings: Embeddings,
        k: int = 5,
    ) -> Self:
        """Constructs retriever asynchronously without blocking during document embedding."""
        retriever = cls.model_construct(
            docs=docs,
            embeddings=embeddings,
            k=k,
        )
        if docs:
            vectors = await embeddings.aembed_documents(
                [doc.page_content for doc in docs]
            )
            retriever._vectors = np.array(vectors)
        else:
            retriever._vectors = np.empty((0, 0))

        return retriever
