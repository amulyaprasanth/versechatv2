import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ConversationStub(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GetConversationsRequest(BaseModel):
    user_id: uuid.UUID


class GetConversationsResponse(BaseModel):
    user_id: uuid.UUID
    conversations: list[ConversationStub]


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationDetail(BaseModel):
    id: uuid.UUID
    title: str
    messages: list[ConversationMessage] = []
