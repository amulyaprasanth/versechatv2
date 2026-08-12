import requests
from langchain.tools import tool


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


if __name__ == "__main__":
    result = bible_search.invoke(input="god is love")
    print(result)
