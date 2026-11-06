import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from tqdm.auto import tqdm

from versechat_backend.core.logger import get_logger

logger = get_logger()

if os.path.exists(".env.dev"):
    load_dotenv(".env.dev")

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

connection = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}"

collection_name = "bible_docs"


class VectorStore:
    """Manages Bible document ingestion and semantic retrieval using PGVector."""

    def __init__(self):
        """Initialize the vector store, embedding model, and Bible directory.

        Args:
            bible_dir_path: Path to the directory containing Bible JSON files.
        """

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.store = PGVector(
            embeddings=self.embeddings,
            collection_name=collection_name,
            connection=connection,
            use_jsonb=True,
            async_mode=True,
        )

    async def setup_store(self, docs: list[Document], ids: list[str]):

        batch_size = 100

        for start in tqdm(
            range(0, len(docs), batch_size),
            desc="Indexing Bible",
            unit="batch",
        ):
            end = start + batch_size

            await self.store.aadd_documents(
                docs[start:end],
                ids=ids[start:end],
            )
