import pytest

from versechat_backend.rag.bible_agent import BibleAgent
from versechat_backend.rag.tools import bible_search


@pytest.mark.anyio
async def test_bible_agent():
    agent = BibleAgent(
        model_name="llama-3.3-70b-versatile",
        tools=[bible_search],
    )

    response = await agent.ask("Who is Jesus?")

    assert isinstance(response, str)
    assert response.strip()
