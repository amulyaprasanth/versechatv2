import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from versechat_backend.core.logger import get_logger
from versechat_backend.database import get_db
from versechat_backend.models.conversations import (
    ConversationDetail,
    ConversationMessage,
    ConversationStub,
    GetConversationsResponse,
)
from versechat_backend.models.db import Conversation, User
from versechat_backend.routers.auth import get_current_user

logger = get_logger()
conversation_router = APIRouter()


class CreateConversationRequest(BaseModel):
    title: str | None = None


@conversation_router.get("/conversations", response_model=GetConversationsResponse)
def get_conversations(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> GetConversationsResponse:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = session.scalars(statement).all()

    return GetConversationsResponse(
        user_id=user.id,
        conversations=[
            ConversationStub(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
            for conversation in conversations
        ],
    )


@conversation_router.post(
    "/conversations",
    response_model=ConversationStub,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
    payload: CreateConversationRequest | None = None,
) -> ConversationStub:
    title = (payload.title if payload and payload.title else "New conversation").strip()
    conversation = Conversation(id=uuid.uuid4(), user_id=user.id, title=title)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return ConversationStub(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@conversation_router.get(
    "/conversations/{conversation_id}", response_model=ConversationDetail
)
@conversation_router.get(
    "/conversation/{conversation_id}", response_model=ConversationDetail
)
async def get_conversation(
    conversation_id: uuid.UUID,
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
):
    stmt = select(Conversation).where(
        and_(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )

    conversation = session.scalars(stmt).one_or_none()

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = []
    try:
        snapshot = await request.app.state.agent.aget_state(
            {"configurable": {"thread_id": f"{conversation.id}:{conversation.user_id}"}}
        )

        if snapshot and snapshot.values:
            for message in snapshot.values.get("messages", []):
                msg_type = getattr(message, "type", None)
                if msg_type == "human":
                    messages.append(
                        ConversationMessage(role="user", content=message.content)
                    )
                elif msg_type == "ai" and not getattr(message, "tool_calls", None):
                    messages.append(
                        ConversationMessage(role="assistant", content=message.content)
                    )
    except Exception as e:
        logger.exception(
            "Could not load agent state for conversation %s", conversation_id
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conversation history is temporarily unavailable",
        ) from e

    return ConversationDetail(
        id=conversation_id, title=conversation.title, messages=messages
    )


@conversation_router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@conversation_router.delete(
    "/conversation/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    conversation = session.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user.id
        )
    )

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        if (
            hasattr(request.app.state, "checkpointer")
            and request.app.state.checkpointer
        ):
            await request.app.state.checkpointer.adelete_thread(
                f"{conversation.id}:{conversation.user_id}"
            )
    except Exception as e:
        logger.exception(
            "Failed to delete thread from checkpointer for conversation %s",
            conversation_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conversation could not be deleted; please try again",
        ) from e

    session.delete(conversation)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
