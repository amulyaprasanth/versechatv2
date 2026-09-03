import os

from dotenv import load_dotenv
from langchain.messages import AnyMessage, HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq

from versechat_backend.rag.states.state import State
from versechat_backend.rag.tools import bible_search, wiki_tool

load_dotenv(".env.dev")


system_prompt = """
    You are VerseChat, an assistant focused on the Bible and Christianity.

You have access to tools for retrieving authoritative information.

Tool usage:
- Use Bible Search for Bible verses, passages, quotations, references,
  and questions where the exact biblical text is important.
- Use Wikipedia for general factual or historical information when
  external information is needed.
- Do not fabricate Bible quotations or references.
- When a tool provides relevant information, base your answer on that
  information.
- If the available tools cannot establish an answer, say so rather than
  inventing information.

Answer the user's question directly and clearly. Always answer in paragraph format do not use tables.
"""


class LLMNode:
    def __init__(
        self, tools: list[BaseTool], model: str = "openai/gpt-oss-20b"
    ) -> None:

        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
        if not os.environ["GROQ_API_KEY"].strip():
            raise ValueError("Groq API key is missing from environment variables")

        try:
            self.llm = ChatGroq(model=model)
            self.llm_with_tools = self.llm.bind_tools(tools)
        except ValueError:
            raise ValueError(
                "Invalid model name. Please check [https://console.groq.com/docs/models](https://console.groq.com/docs/models) for a list of supported models."
            )

    def get_node(self, state: State) -> State:

        messages: list[AnyMessage] = [SystemMessage(content=system_prompt)]
        messages.extend(state["messages"])
        return {"messages": [self.llm_with_tools.invoke(messages)]}


if __name__ == "__main__":
    node = LLMNode(tools=[bible_search, wiki_tool])

    state = State({"messages": [HumanMessage(content="who is jesus")]})
    print(node.get_node(state))
