from unittest.mock import Mock, patch

from langchain.messages import AIMessage
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from versechat_backend.rag.wiki_retriever import WikiRetriever

# Importing tools constructs WikiRetriever eagerly. Skip only its expensive
# embedding initialization while importing the real, correctly typed tools.
with patch.object(WikiRetriever, "__init__", return_value=None):
    from versechat_backend.rag.graph.graph_builder import GraphBuilder


def build_graph_builder():
    return GraphBuilder(checkpointer=MemorySaver())


@patch("versechat_backend.rag.graph.graph_builder.LLMNode")
def test_build_graph_returns_compiled_graph(mock_llm_node):
    mock_node = Mock()
    mock_llm_node.return_value.get_node.return_value = mock_node

    graph_builder = build_graph_builder()
    graph = graph_builder.build_graph()

    assert graph is not None


@patch("versechat_backend.rag.graph.graph_builder.LLMNode")
def test_graph_has_llm_node(mock_llm_node):
    mock_node = Mock()

    mock_llm_node.return_value.get_node.return_value = mock_node

    graph_builder = build_graph_builder()
    graph = graph_builder.build_graph()
    graph_structure = graph.get_graph()

    assert "llm" in graph_structure.nodes
    assert "tool_node" in graph_structure.nodes


@patch("versechat_backend.rag.graph.graph_builder.LLMNode")
def test_graph_invokes_llm_node(mock_llm_node):
    def fake_llm_node(state):
        return {
            "messages": [
                AIMessage(content="Test response"),
            ]
        }

    mock_llm_node.return_value.get_node = fake_llm_node

    graph = build_graph_builder().build_graph()

    result = graph.invoke(
        {"messages": [HumanMessage(content="Who is Jesus?")]},
        {"configurable": {"thread_id": "1"}},
    )

    assert result["messages"]
    assert len(result["messages"]) == 2
    assert result["messages"][-1].content == "Test response"
