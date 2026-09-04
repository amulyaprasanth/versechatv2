import operator
from typing import Annotated

from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
