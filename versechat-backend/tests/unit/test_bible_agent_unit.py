from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain.messages import ToolMessage

from versechat_backend.rag.bible_agent import BibleAgent
from versechat_backend.rag.tools import bible_search


@patch("versechat_backend.rag.bible_agent.create_agent")
@patch("versechat_backend.rag.bible_agent.ChatGroq")
@patch.dict("os.environ", {"GROQ_API_KEY": "test-api-key"})
def test_bibleagent_initialization(
    mock_chatgroq,
    mock_create_agent,
):
    mock_model = Mock()
    mock_chatgroq.return_value = mock_model

    mock_agent = Mock()
    mock_create_agent.return_value = mock_agent

    agent = BibleAgent(
        model_name="llama-3.3-70b-versatile",
        tools=[bible_search],
    )

    mock_chatgroq.assert_called_once()

    call_kwargs = mock_chatgroq.call_args.kwargs

    assert call_kwargs["model"] == "llama-3.3-70b-versatile"
    assert call_kwargs["api_key"].get_secret_value() == "test-api-key"

    mock_create_agent.assert_called_once_with(
        model=mock_model,
        tools=[bible_search],
        system_prompt=agent.prompt_template,
    )

    assert agent.model_name == "llama-3.3-70b-versatile"
    assert agent.tools == [bible_search]
    assert agent.model is mock_model
    assert agent.agent is mock_agent


def test_bible_agent_empty_model_name():
    with pytest.raises(ValueError, match="model_name is empty"):
        BibleAgent(model_name="", tools=[bible_search])


def test_bible_agent_invalid_tools():
    with pytest.raises(
        ValueError, match="No tools to bind the model. Tools list is empty"
    ):
        BibleAgent(model_name="llama-3.3-70b-versatile", tools=[])


@patch("versechat_backend.rag.bible_agent.ChatGroq")
@patch("versechat_backend.rag.bible_agent.create_agent")
def test_bible_agent_invalid_model_name(mock_create_agent, mock_chatgroq):
    mock_chatgroq.side_effect = ValueError(
        "Invalid model name. Please check "
        "[https://console.groq.com/docs/models]"
        "(https://console.groq.com/docs/models) "
        "for a list of supported models."
    )

    with pytest.raises(ValueError, match=r"Invalid model name\. Please check"):
        BibleAgent(
            model_name="some_llm_model",
            tools=[bible_search],
        )

    mock_chatgroq.assert_called_once()
    mock_create_agent.assert_not_called()


@patch.dict("os.environ", {"GROQ_API_KEY": "test-api-key"})
@patch("versechat_backend.rag.bible_agent.ChatGroq")
@patch("versechat_backend.rag.bible_agent.create_agent")
def test_bible_agent_groq_env(mock_create_agent, mock_chatgroq):
    mock_chatgroq.return_value = Mock()
    mock_create_agent.return_value = Mock()

    agent = BibleAgent(
        model_name="llama-3.3-70b-versatile",
        tools=[bible_search],
    )

    assert agent.groq_api_key == "test-api-key"


@patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=True)
def test_bible_agent_missing_groq_api_key():
    with pytest.raises(ValueError, match="GROQ_API_KEY is missing"):
        BibleAgent(
            model_name="llama-3.3-70b-versatile",
            tools=[bible_search],
        )


@pytest.mark.anyio
@patch.dict("os.environ", {"GROQ_API_KEY": "test-api-key"})
async def test_bible_agent_ask_success():
    tool_msg = ToolMessage(
        content="John 3:16 details",
        tool_call_id="call_123",
        name="bible_search",
    )
    ai_msg = Mock(content="Jesus is the Son of God.")

    mock_agent = Mock()
    mock_agent.ainvoke = AsyncMock(return_value={"messages": [tool_msg, ai_msg]})
    agent = BibleAgent(
        model_name="llama-3.3-70b-versatile",
        tools=[bible_search],
    )
    agent.agent = mock_agent

    answer, sources = await agent.ask("Who is Jesus")

    mock_agent.ainvoke.assert_awaited_once_with(
        {"messages": [{"role": "user", "content": "Who is Jesus"}]}
    )
    assert answer == "Jesus is the Son of God."
    assert sources == [
        {
            "tool_name": "bible_search",
            "tool_output": "John 3:16 details",
        }
    ]


@pytest.mark.anyio
@patch.dict("os.environ", {"GROQ_API_KEY": "test-api-key"})
async def test_bible_agent_ask_query_empty():
    mock_agent = Mock()
    mock_agent.ainvoke = AsyncMock()

    agent = BibleAgent(
        model_name="llama-3.3-70b-versatile",
        tools=[bible_search],
    )
    agent.agent = mock_agent

    with pytest.raises(ValueError, match="query should not be empty"):
        await agent.ask("")

    mock_agent.ainvoke.assert_not_awaited()


@pytest.mark.anyio
@patch.dict("os.environ", {"GROQ_API_KEY": "test-api-key"})
async def test_bible_agent_ask_runtime_error():
    mock_agent = Mock()
    mock_agent.ainvoke = AsyncMock(side_effect=RuntimeError("Agent invocation failed"))

    agent = BibleAgent(
        model_name="llama-3.3-70b-versatile",
        tools=[bible_search],
    )
    agent.agent = mock_agent

    answer, sources = await agent.ask("Who is Jesus?")

    assert answer == "Sorry, something went wrong while processing your request."
    assert sources == []

    mock_agent.ainvoke.assert_awaited_once_with(
        {"messages": [{"role": "user", "content": "Who is Jesus?"}]}
    )
