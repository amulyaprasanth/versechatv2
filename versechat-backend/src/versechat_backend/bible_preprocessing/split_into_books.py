import json
import os

from versechat_backend.bible_preprocessing.utils import load_json
from versechat_backend.core.logger import get_logger

logger = get_logger()


def main():
    # load the single json
    content = load_json("bible/raw/en_kjv.json")

    # create a file for every chapter and save it in a folder
    os.makedirs("bible/books", exist_ok=True)

    write_bible_to_json(content)


def write_bible_to_json(books: list[dict]):
    """Given a list of bible books containing name and chapter as key, will create a separate json for each book in bible as bookname.json"""

    for book in books:
        write_book_to_json(book)


def write_book_to_json(book: dict):
    """Given a dictionary with name and chapters, this writes a json file to the bible directory"""
    logger.info(f"Writing {book['name']} to json")
    with open(f"bible/books/{book['name']}.json", "w") as f:
        json.dump(book, f)


if __name__ == "__main__":
    main()
