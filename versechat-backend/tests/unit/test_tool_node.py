from unittest.mock import Mock

import pytest
from langchain.messages import AIMessage, ToolMessage

from versechat_backend.rag.nodes.tool_node import ToolNode
from versechat_backend.rag.states.state import State


def test_tool_node_executes_tool_call():
    # Arrange
    tool = Mock()
    tool.invoke.return_value = "Bible search result"

    node = ToolNode(
        tools_by_name={
            "bible_search": tool,
        }
    )

    state: State = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "bible_search",
                        "args": {"query": "John 3:16"},
                        "id": "call_123",
                        "type": "tool_call",
                    }
                ],
            )
        ]
    }

    # Act
    result = node.tool_node(state)

    # Assert
    tool.invoke.assert_called_once_with({"query": "John 3:16"})

    assert len(result["messages"]) == 1

    message = result["messages"][0]

    assert isinstance(message, ToolMessage)
    assert message.content == "Bible search result"
    assert message.tool_call_id == "call_123"


def test_tool_node_executes_multiple_tool_calls():
    # Arrange
    bible_tool = Mock()
    bible_tool.invoke.return_value = "John 3:16 passage"

    wiki_tool = Mock()
    wiki_tool.invoke.return_value = "Wikipedia result"

    node = ToolNode(
        tools_by_name={
            "bible_search": bible_tool,
            "wiki": wiki_tool,
        }
    )

    state: State = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "bible_search",
                        "args": {"query": "John 3:16"},
                        "id": "call_1",
                        "type": "tool_call",
                    },
                    {
                        "name": "wiki",
                        "args": {"query": "Christianity"},
                        "id": "call_2",
                        "type": "tool_call",
                    },
                ],
            )
        ]
    }

    # Act
    result = node.tool_node(state)

    # Assert
    bible_tool.invoke.assert_called_once_with({"query": "John 3:16"})
    wiki_tool.invoke.assert_called_once_with({"query": "Christianity"})

    assert len(result["messages"]) == 2

    if isinstance(result["messages"][0], ToolMessage):
        assert result["messages"][0].tool_call_id == "call_1"
    assert result["messages"][0].content == "John 3:16 passage"

    if isinstance(result["messages"][1], ToolMessage):
        assert result["messages"][1].tool_call_id == "call_2"
    assert result["messages"][1].content == "Wikipedia result"


def test_tool_node_requires_ai_message():
    node = ToolNode(tools_by_name={})

    state: State = {
        "messages": [
            ToolMessage(
                content="previous result",
                tool_call_id="call_123",
            )
        ]
    }

    with pytest.raises(TypeError, match="ToolNode requires an AIMessage"):
        node.tool_node(state)
