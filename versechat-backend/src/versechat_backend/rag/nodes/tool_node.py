from langchain.messages import AIMessage, AnyMessage, ToolMessage

from versechat_backend.rag.states.state import State


class ToolNode:
    def __init__(self, tools_by_name):
        self.tools_by_name = tools_by_name

    def tool_node(self, state: State) -> State:
        """Performs the tool call."""

        last_message = state["messages"][-1]

        if not isinstance(last_message, AIMessage):
            raise TypeError("ToolNode requires an AIMessage")

        result: list[AnyMessage] = []

        for tool_call in last_message.tool_calls:
            tool = self.tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])

            result.append(
                ToolMessage(
                    content=str(observation),
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": result}
