import requests
from langchain.tools import tool
import wikipediaapi


wiki = wikipediaapi.Wikipedia(
    user_agent="Versechat/1.0 (amulyaprasanth301@gmail.com)", language="en"
)


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
    "wikipedia_tool",
    description="Search Wikipedia for historical and archaeological information."
)
def wikipedia_search(query: str) -> str:
    """Search Wikipedia and return the article content."""

    if not query or not query.strip():
        return "Invalid query"

    try:
        page = wiki.page(query)

        if not page.exists():
            return f"No Wikipedia page was found for '{query}'."

        return page.text

    except wikipediaapi.exceptions.WikiConnectionError:
        return "Could not connect to Wikipedia"

    except wikipediaapi.exceptions.WikiHttpTimeoutError:
        return "The request to Wikipedia timed out"

    except wikipediaapi.exceptions.WikiRateLimitError:
        return "Wikipedia rate limit was exceeded"

    except wikipediaapi.exceptions.WikiInvalidJsonError:
        return "Wikipedia returned an invalid JSON response"

    except wikipediaapi.exceptions.WikiHttpError as e:
        return f"Wikipedia HTTP error: {e}"
if __name__ == "__main__":
    result = bible_search.invoke(input="god is love")
    print(result)
