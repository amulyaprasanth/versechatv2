import json
import os

from versechat_backend.bible_preprocessing.utils import load_json
from versechat_backend.core.logger import get_logger

logger = get_logger()


def main():
    annotate_bible()


def annotate_bible(bible_dir_path: str = "./bible/books"):
    """Iterates over all the books and calls annotate book fn"""
    files = os.listdir(bible_dir_path)

    for file in files:
        annotate_book(bible_dir_path, file)


def annotate_book(bible_path: str, book_json: str):
    """Annotates verse with verse number and chapter number"""
    new_chapters = []
    json_path = f"{bible_path}/{book_json}"
    book = load_json(json_path)
    chapters = book["chapters"]

    for idx, chapter in enumerate(chapters):
        new_chapters.append(
            annotate_chapter(chapter, idx + 1)
        )  # plus 1 because indexing starts at 0

    book["chapters"] = new_chapters

    logger.info(f"Updating {book['name']} with new references")

    with open(json_path, "w") as f:
        json.dump(book, f)


def annotate_chapter(chapter: list, chapter_number: int):
    new_chapter = []

    for idx, verse in enumerate(chapter):
        new_chapter.append({"text": verse, "chapter": chapter_number, "verse": idx + 1})
    return new_chapter


if __name__ == "__main__":
    main()
