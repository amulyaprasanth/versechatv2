import asyncio

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from versechat_backend.rag.retriever import InMemoryRetriever
from versechat_backend.rag.wiki import wikipedia_search


class WikiRetriever:
    def __init__(self, default_k: int = 5):
        self.default_k = default_k
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def invoke(self, query: str, topic: str) -> list[Document]:
        content = wikipedia_search(topic)

        if not content or not content.strip():
            return []

        split_content = self.splitter.split_documents([Document(page_content=content)])

        retriever = InMemoryRetriever(
            docs=split_content, embeddings=self.embeddings, k=self.default_k
        )

        docs = retriever.invoke(query)

        return docs

    async def ainvoke(self, query: str, topic: str) -> list[Document]:
        # 1. Non-blocking wikipedia fetch
        content = await asyncio.to_thread(wikipedia_search, topic)

        if not content or not content.strip():
            return []

        # 2. Chunk text
        split_content = self.splitter.split_documents([Document(page_content=content)])

        # 3. Non-blocking async vectorization via factory constructor
        retriever = await InMemoryRetriever.afrom_documents(
            docs=split_content, embeddings=self.embeddings, k=self.default_k
        )

        # 4. Non-blocking similarity search
        docs = await retriever.ainvoke(query)

        return docs
