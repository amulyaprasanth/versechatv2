from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class Source(BaseModel):
    tool_name: str
    tool_output: str


class ChatResponse(BaseModel):
    id: UUID
    role: str
    content: str


#   sources: list[Source]
