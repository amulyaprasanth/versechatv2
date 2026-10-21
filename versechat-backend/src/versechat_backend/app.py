import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy import select
from sqlalchemy.orm import Session

from versechat_backend.core.logger import get_logger
from versechat_backend.database import (
    Base,
    build_langgraph_database_url,
    engine,
    get_db,
)
from versechat_backend.models.chat import ChatRequest, ChatResponse
from versechat_backend.models.db import Conversation, User
from versechat_backend.rag.conversation_title import generate_conversation_title
from versechat_backend.rag.graph.graph_builder import GraphBuilder
from versechat_backend.routers.auth import get_current_user
from versechat_backend.routers.auth import router as auth_router
from versechat_backend.routers.conversations import conversation_router

logger = get_logger()
_title_refinement_tasks: set[asyncio.Task[None]] = set()
NEW_CONVERSATION_TITLE = "New conversation"


def ensure_conversation(
    session: Session,
    conversation_id: uuid.UUID,
    user: User,
) -> Conversation:
    conversation = session.scalar(
        select(Conversation).where(Conversation.id == conversation_id)
    )

    if conversation is None:
        conversation = Conversation(id=conversation_id, user_id=user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    elif conversation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        async with AsyncPostgresSaver.from_conn_string(
            build_langgraph_database_url()
        ) as checkpointer:
            await checkpointer.setup()
            app.state.checkpointer = checkpointer
            app.state.agent = GraphBuilder(checkpointer).build_graph()
            try:
                yield
            finally:
                engine.dispose()
    except Exception:
        logger.exception("Application failed to initialize")
        raise


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(conversation_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=200)
async def get_health():
    return JSONResponse({"message": "healthy"})


async def _refine_conversation_title(conv_id: uuid.UUID, query: str):
    try:
        refined_title = await generate_conversation_title(query)
        with Session(engine) as session:
            conv = session.scalar(
                select(Conversation).where(Conversation.id == conv_id)
            )
            if conv:
                conv.title = refined_title
                session.commit()
    except Exception as e:  # noqa: BLE001
        logger.warning("Could not generate title for conversation %s: %s", conv_id, e)


def _schedule_title_refinement(conv_id: uuid.UUID, query: str) -> None:
    task = asyncio.create_task(_refine_conversation_title(conv_id, query))
    _title_refinement_tasks.add(task)
    task.add_done_callback(_title_refinement_tasks.discard)


@app.post(
    "/ask/stream",
    responses={404: {"description": "Conversation not found"}},
)
async def stream_message(
    request: ChatRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
):
    conversation = ensure_conversation(session, request.conv_id, user)
    should_refine = False
    if conversation.title in (NEW_CONVERSATION_TITLE, "", None):
        conversation.title = request.query[:60].strip() or NEW_CONVERSATION_TITLE
        should_refine = True
    conversation.updated_at = datetime.now(UTC)
    session.commit()

    if should_refine:
        _schedule_title_refinement(conversation.id, request.query)

    agent = app.state.agent

    async def generate():
        async for chunk in agent.astream(
            {"messages": [HumanMessage(content=request.query)]},
            {"configurable": {"thread_id": f"{request.conv_id}:{user.id}"}},
            stream_mode=["messages"],
            version="v2",
        ):
            if chunk["type"] == "messages":
                message_chunk, metadata = chunk["data"]
                if metadata["langgraph_node"] == "llm" and message_chunk.content:
                    yield message_chunk.content

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


@app.post(
    "/ask",
    responses={404: {"description": "Conversation not found"}},
)
async def ask_agent(
    request: ChatRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> ChatResponse:
    conversation = ensure_conversation(session, request.conv_id, user)
    should_refine = False
    if conversation.title in (NEW_CONVERSATION_TITLE, "", None):
        conversation.title = request.query[:60].strip() or NEW_CONVERSATION_TITLE
        should_refine = True
    conversation.updated_at = datetime.now(UTC)
    session.commit()

    if should_refine:
        _schedule_title_refinement(conversation.id, request.query)

    agent = app.state.agent

    try:
        messages = {"messages": [HumanMessage(content=request.query)]}

        response = await agent.ainvoke(
            messages,
            {"configurable": {"thread_id": f"{request.conv_id}:{user.id}"}},
        )

        answer = response["messages"][-1].content

    except Exception:
        logger.exception("failed to serve user request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal error occured",
        )

    return ChatResponse(id=uuid.uuid4(), role="assistant", content=answer)
