import asyncio
import os

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm.auto import tqdm

from versechat_backend.bible_preprocessing.utils import load_json


class VectorStore:
    def __init__(self, bible_dir_path: str):
        self.bible_dir_path = bible_dir_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.vectorstore = InMemoryVectorStore(embedding=self.embeddings)

    async def load_bible(self):
        files = [
            os.path.join(self.bible_dir_path, filename)
            for filename in os.listdir(self.bible_dir_path)
            if filename.endswith(".json")
        ]

        tasks = [asyncio.to_thread(self.load_book, filepath) for filepath in files]

        for task in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc="Loading Bible",
        ):
            docs = await task
            await self.vectorstore.aadd_documents(docs)

    def load_book(self, book_path: str) -> list[Document]:
        """
        Loads a book in bible into langchain document format
        """
        docs = []
        book_dict = load_json(book_path)

        name = book_dict["name"]
        for chapter in book_dict["chapters"]:
            for verse in chapter:
                docs.append(
                    Document(
                        page_content=verse["text"],
                        metadata={
                            "book_name": name,
                            "chapter": verse["chapter"],
                            "verse": verse["verse"],
                        },
                    )
                )

        return docs


def main():
    bible_path = "./bible/books"

    # create the directory loader
    vectorstore = VectorStore(bible_path)
    asyncio.run(vectorstore.load_bible())
    vs = vectorstore.vectorstore

    print(vs.similarity_search("god is love"))


if __name__ == "__main__":
    main()
