from typing import Literal

from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from versechat_backend.core.logger import get_logger
from versechat_backend.rag.nodes.llm_node import LLMNode
from versechat_backend.rag.nodes.tool_node import ToolNode
from versechat_backend.rag.states.state import State
from versechat_backend.rag.tools import bible_search, wiki_tool

logger = get_logger()


class GraphBuilder:
    def __init__(self):
        self.tools = [bible_search, wiki_tool]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.builder = StateGraph(State)
        self.llm_node = LLMNode(self.tools).get_node
        self.tool_node = ToolNode(self.tools_by_name).tool_node

    def should_continue(self, state: State) -> Literal["tool_node", "end"]:

        messages = state["messages"]
        last_message = messages[-1]

        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tool_node"

        return "end"

    def build_graph(self):
        logger.info("building graph....")
        self.builder.add_node("llm", self.llm_node)
        self.builder.add_node("tool_node", self.tool_node)

        self.builder.add_edge(START, "llm")
        self.builder.add_conditional_edges(
            "llm", self.should_continue, {"tool_node": "tool_node", "end": END}
        )
        self.builder.add_edge("tool_node", "llm")

        return self.builder.compile()


if __name__ == "__main__":
    import asyncio

    graph = GraphBuilder().build_graph()

    # messages = graph.invoke({"messages": [HumanMessage(content="who is jesus?")]})
    async def main():
        async for chunk in graph.astream(
            {"messages": [HumanMessage(content="who is jesus?")]},
            stream_mode=["messages"],
            version="v2",
        ):
            if chunk["type"] == "messages":
                message_chunk, metadata = chunk["data"]

                if metadata["langgraph_node"] == "llm" and message_chunk.content:
                    print(message_chunk.content, end="|", flush=True)

    asyncio.run(main())
