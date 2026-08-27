import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    user_agent="Versechat/1.0 (amulyaprasanth301@gmail.com)", language="en"
)


def wikipedia_search(topic: str) -> str:
    """Search Wikipedia and return the article content."""

    if not topic or not topic.strip():
        return "Invalid topic"

    try:
        page = wiki.page(topic)

        if not page.exists():
            return f"No Wikipedia page was found for '{topic}'."

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
