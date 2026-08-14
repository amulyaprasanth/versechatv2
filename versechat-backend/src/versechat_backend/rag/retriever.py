import numpy as np
from langchain.embeddings import Embeddings
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import PrivateAttr


class InMemoryRetriever(BaseRetriever):
    docs: list[Document]
    embeddings: Embeddings
    k: int = 5

    _vectors: np.ndarray = PrivateAttr()

    def model_post_init(self, __context, /) -> None:
        self._vectors = np.array(
            self.embeddings.embed_documents([doc.page_content for doc in self.docs])
        )

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


if __name__ == "__main__":
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    from versechat_backend.rag.tools import wikipedia_search

    result = Document(page_content=wikipedia_search.invoke("jerusalem"))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )

    split_results = splitter.split_documents([result])

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    retriever = InMemoryRetriever(
        docs=split_results,
        embeddings=embeddings,
        k=5,
    )

    results = retriever.invoke("historical significance of Jerusalem")

    for result in results:
        print(result.page_content)
        print("-" * 80)
