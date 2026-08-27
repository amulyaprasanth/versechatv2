from unittest.mock import Mock, patch

from versechat_backend.rag.tools import bible_search


@patch("versechat_backend.rag.tools.requests.get")
def test_bible_search_success(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = [
        {
            "book": "John",
            "chapter": 3,
            "verse": 16,
            "text": "For God so loved the world...",
        }
    ]

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = bible_search.invoke("god is love")

    assert result == [
        {
            "book": "John",
            "chapter": 3,
            "verse": 16,
            "text": "For God so loved the world...",
        }
    ]

    mock_get.assert_called_once()


@patch("versechat_backend.rag.tools.requests.get")
def test_bible_search_empty_query(mock_get):
    result = bible_search.invoke("")

    assert result == [{"error": "Invalid query provided."}]

    mock_get.assert_not_called()


@patch("versechat_backend.rag.tools.requests.get")
def test_bible_search_unexpected_response_format(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {"results": []}

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = bible_search.invoke("god is love")

    assert result == [{"error": "Unexpected API response format."}]


@patch("versechat_backend.rag.tools.requests.get")
def test_bible_search_request_error(mock_get):
    import requests

    mock_get.side_effect = requests.exceptions.Timeout()

    result = bible_search.invoke("god is love")

    assert result == [{"error": "Request failed: "}]


@patch("versechat_backend.rag.tools.requests.get")
def test_bible_search_http_error(mock_get):
    import requests

    mock_response = Mock()

    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )

    mock_get.return_value = mock_response

    result = bible_search.invoke("god is love")

    assert result == [{"error": "Request failed: 500 Server Error"}]
