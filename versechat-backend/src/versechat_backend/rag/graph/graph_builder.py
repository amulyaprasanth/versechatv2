from langchain.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from versechat_backend.rag.nodes.llm_node import LLMNode
from versechat_backend.rag.states.state import State


class GraphBuilder:
    def __init__(self):
        self.builder = StateGraph(State)
        self.llm_node = LLMNode().get_node

    def build_graph(self):
        self.builder.add_node("llm", self.llm_node)

        self.builder.add_edge(START, "llm")
        self.builder.add_edge("llm", END)

        return self.builder.compile()


if __name__ == "__main__":
    graph = GraphBuilder().build_graph()

    messages = graph.invoke({"messages": [HumanMessage(content="who is jesus?")]})
    for message in messages["messages"]:
        message.pretty_print()
