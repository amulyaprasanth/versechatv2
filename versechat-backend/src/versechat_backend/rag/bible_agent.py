import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

load_dotenv(".env.dev")

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "").strip('"')


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


model = ChatGroq(model="openai/gpt-oss-20b")

# create llm node


def llm_node(state: dict):
    return {
        "messages": [
            model.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant. Answer the user's questions. DO NOT answer in markdown format"
                    )
                ]
                + state["messages"]
            )
        ]
    }


agent_builder = StateGraph(MessagesState)
agent_builder.add_node(llm_node, "llm_node")
agent_builder.add_edge(START, "llm_node")
agent_builder.add_edge("llm_node", END)

# compile the agent
agent = agent_builder.compile()


# Invoke
messages = [HumanMessage(content="what is the capital of India?")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()
