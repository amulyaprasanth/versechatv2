import os

import bm25s
import Stemmer
from langchain_core.documents import Document

from versechat_backend.core.logger import get_logger

logger = get_logger()


class BM25Retriever:
    def __init__(
        self,
        lang: str = "english",
    ):
        if lang == "english":
            self.corpus_lang = "en"

        self.stemmer = Stemmer.Stemmer(lang)

    def tokenize_corpus(self, documents: list[Document]):
        """Converts langchain documents into tokenized corpus for bm25"""
        if len(documents) == 0:
            logger.warning("Corpus is empty")
            return []

        corpus = [doc.page_content for doc in documents]
        return bm25s.tokenize(corpus, stopwords=self.corpus_lang, stemmer=self.stemmer)

    def create_retriever(
        self,
        documents: list[Document],
        save_index: bool = False,
        save_path: str = "artifacts/bm25_index",
    ):
        """Creates and optionally saves a BM25 index."""
        tokenized_corpus = self.tokenize_corpus(documents)

        if not tokenized_corpus:
            raise ValueError("Cannot create BM25 index from an empty corpus")

        bm25_retriever = bm25s.BM25()

        logger.info("Adding documents to index")
        bm25_retriever.index(tokenized_corpus)
        logger.info("Indexing complete")

        if save_index:
            parent_dir = os.path.dirname(save_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            bm25_retriever.save(save_path)

        return bm25_retriever

    def load_index(self, index_path: str = "artifacts/bm25_index"):
        """Loads Index from the given path and returns the loaded retriever"""
        return bm25s.BM25.load(index_path, load_corpus=True)
