from typing import Literal

from langchain.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt.tool_node import ToolNode

from versechat_backend.core.logger import get_logger
from versechat_backend.rag.nodes.llm_node import LLMNode
from versechat_backend.rag.states.state import State
from versechat_backend.rag.tools import bible_search, wiki_tool

logger = get_logger()


class GraphBuilder:
    def __init__(self):
        self.tools = [bible_search, wiki_tool]
        self.builder = StateGraph(State)
        self.llm_node = LLMNode(self.tools).get_node
        self.tool_node = ToolNode(self.tools)
        self.checkpointer = InMemorySaver()

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

        return self.builder.compile(checkpointer=self.checkpointer)


if __name__ == "__main__":
    import asyncio
    import os

    from dotenv import load_dotenv

    load_dotenv()

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
    os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")

    graph = GraphBuilder().build_graph()

    async def main():
        async for chunk in graph.astream(
            {"messages": [HumanMessage(content="god is love")]},
            {
                "configurable": {"thread_id": "1"},
            },
            stream_mode=["messages"],
            version="v2",
        ):
            if chunk["type"] == "messages":
                message_chunk, metadata = chunk["data"]

                if metadata["langgraph_node"] == "llm" and message_chunk.content:
                    print(message_chunk.content, end="|", flush=True)

    asyncio.run(main())
