from unittest.mock import Mock, patch
import wikipediaapi

from versechat_backend.rag.tools import wikipedia_search

@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_success(mock_page):
    mock_response = Mock()
    
    mock_response.exists.return_value = True
    mock_response.text = "Python is an interpreted programming language"
    
    mock_page.return_value = mock_response

    result = wikipedia_search.invoke('Python')
    
    mock_page.assert_called_once_with("Python")
    assert result == "Python is an interpreted programming language"
    
@patch("versechat_backend.rag.tools.wiki.page")
def test_wki_tool_empty_query(mock_page):
    result = wikipedia_search.invoke("")
    
    assert result == "Invalid query"
    mock_page.assert_not_called()
    
    
@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_page_not_exist(mock_page):
    mock_response = Mock()
    mock_response.exists.return_value = False
    mock_page.return_value = mock_response
    result = wikipedia_search.invoke("$%#")
    
    mock_page.assert_called_once_with("$%#")
    assert result == f"No Wikipedia page was found for '$%#'."
    
@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_connection_error(mock_page):
    
    mock_page.side_effect = wikipediaapi.exceptions.WikiConnectionError("https://wiki.org/machine-learning")
    
    
    result = wikipedia_search.invoke("machine learning")
    
    mock_page.assert_called_once_with("machine learning")
    assert result == "Could not connect to Wikipedia"
    
@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_timeout_error(mock_page):
    mock_page.side_effect = wikipediaapi.exceptions.WikiHttpTimeoutError(
        "https://wiki.org/machine-learning"
    )

    result = wikipedia_search.invoke("machine learning")

    mock_page.assert_called_once_with("machine learning")
    assert result == "The request to Wikipedia timed out"


@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_rate_limit_error(mock_page):
    mock_page.side_effect = wikipediaapi.exceptions.WikiRateLimitError(
        "https://wiki.org/machine-learning",
        retry_after=30
    )

    result = wikipedia_search.invoke("machine learning")

    mock_page.assert_called_once_with("machine learning")
    assert result == "Wikipedia rate limit was exceeded"


@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_invalid_json_error(mock_page):
    mock_page.side_effect = wikipediaapi.exceptions.WikiInvalidJsonError(
        "https://wiki.org/machine-learning"
    )

    result = wikipedia_search.invoke("machine learning")

    mock_page.assert_called_once_with("machine learning")
    assert result == "Wikipedia returned an invalid JSON response"


@patch("versechat_backend.rag.tools.wiki.page")
def test_wiki_tool_http_error(mock_page):
    mock_page.side_effect = wikipediaapi.exceptions.WikiHttpError(
        500,
        "https://wiki.org/machine-learning"
    )

    result = wikipedia_search.invoke("machine learning")

    mock_page.assert_called_once_with("machine learning")
    assert result == (
        "Wikipedia HTTP error: "
        "(500, 'https://wiki.org/machine-learning')"
    )