import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain.messages import HumanMessage

from versechat_backend.core.logger import get_logger
from versechat_backend.database import Base, engine
from versechat_backend.models.chat import ChatRequest, ChatResponse
from versechat_backend.models.db import User
from versechat_backend.rag.graph.graph_builder import GraphBuilder
from versechat_backend.routers.auth import get_current_user
from versechat_backend.routers.auth import router as auth_router

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        app.state.agent = GraphBuilder().build_graph()
    except Exception:
        logger.exception("Application failed to initialize")
        raise

    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

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


@app.post("/ask/stream")
async def stream_message(
    request: ChatRequest, user: Annotated[User, Depends(get_current_user)]
):

    agent = app.state.agent

    async def generate():
        async for chunk in agent.astream(
            {"messages": [HumanMessage(content=request.query)]},
            {"configurable": {"thread_id": request.conv_id}},
            stream_mode=["messages"],
            version="v2",
        ):
            if chunk["type"] == "messages":
                message_chunk, metadata = chunk["data"]
                if metadata["langgraph_node"] == "llm" and message_chunk.content:
                    yield message_chunk.content

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


@app.post("/ask", response_model=ChatResponse)
async def ask_agent(
    request: ChatRequest, user: Annotated[User, Depends(get_current_user)]
):
    agent = app.state.agent

    try:
        messages = {"messages": [HumanMessage(content=request.query)]}

        response = agent.invoke(
            messages, {"configurable": {"thread_id": request.conv_id}}
        )

        answer = response["messages"][-1].content

    except Exception:
        logger.exception("failed to serve user request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal error occured",
        )

    return ChatResponse(id=uuid.uuid4(), role="assistant", content=answer)
