import requests
from langchain.tools import tool
from pydantic import BaseModel, Field

from versechat_backend.rag.wiki_retriever import WikiRetriever


class WikiSearchInput(BaseModel):
    topic: str = Field(
        description="The Wikipedia article topic/title to search (e.g., 'Jerusalem', 'Quantum computing')"
    )
    query: str = Field(
        description="The specific search question or query to answer using the Wikipedia article content."
    )


retriever = WikiRetriever()


@tool(
    "bible_search",
    description="Performs vector similarity search on bible vector store and returns the results",
)
def bible_search(query: str) -> list[dict]:
    """Perform a semantic Bible search or fetch a verse by reference."""
    if not isinstance(query, str) or not query.strip():
        return [{"error": "Invalid query provided."}]

    try:
        response = requests.get(
            f"https://bible-search.antioch.tech/api/search?verse_query={query}",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            return data
        else:
            return [{"error": "Unexpected API response format."}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Request failed: {e}"}]
    except RuntimeError as e:
        return [{"error": f"Unexpected error: {e}"}]


@tool(
    "wiki_retriever",
    description="Search wikipedia for historical and archaeological information",
)
async def wiki_tool(topic: str, query: str) -> str:
    """Userful for retrieving factual context from Wikipedia for a specific topic"""

    docs = retriever.invoke(query=query, topic=topic)

    if not docs:
        return "No relavant information found on Wikipedia for this topic."

    return "\n\n".join([doc.page_content for doc in docs])


if __name__ == "__main__":
    result = wiki_tool.invoke(
        input="What is the historical significance of Jerusalem in ancient times?"
    )
    print(result)
