import asyncio

from langchain.tools import tool
from pydantic import BaseModel, Field

from versechat_backend.rag.hybrid_search import HybridSearch
from versechat_backend.rag.wiki_retriever import WikiRetriever


class WikiSearchInput(BaseModel):
    topic: str = Field(
        description="The Wikipedia article topic/title to search (e.g., 'Jerusalem', 'Quantum computing')"
    )
    query: str = Field(
        description="The specific search question or query to answer using the Wikipedia article content."
    )


hybrid_search = asyncio.run(HybridSearch.create())
retriever = WikiRetriever()


@tool(
    "bible_search",
    description="Search the Bible for relevant verses.",
    response_format="content_and_artifact",
)
async def bible_search(query: str):
    """Searches the Bible using hybrid retrieval."""

    results = await hybrid_search.ahybrid_search(query)

    if not results:
        return "No relevant Bible verses found.", []

    formatted_results = []

    for doc in results:
        metadata = doc.metadata

        book = metadata.get("book_name", "Unknown")
        chapter = metadata.get("chapter", "")
        verse = metadata.get("verse", "")

        reference = f"{book} {chapter}:{verse}"

        formatted_results.append(f"Reference: {reference}\nVerse: {doc.page_content}")

    content = "\n\n".join(formatted_results)

    return content, results


@tool(
    "wiki_retriever",
    description="Search wikipedia for historical and archaeological information",
)
async def wiki_tool(topic: str, query: str) -> str:
    """Userful for retrieving factual context from Wikipedia for a specific topic"""

    docs = await retriever.ainvoke(query=query, topic=topic)

    if not docs:
        return "No relavant information found on Wikipedia for this topic."

    return "\n\n".join([doc.page_content for doc in docs])


if __name__ == "__main__":
    # result = wiki_tool.invoke(
    #     input="What is the historical significance of Jerusalem in ancient times?"
    # )
    # print(result)
    result = bible_search.invoke("john 3 16")
    print(result)
