import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from versechat_backend.core.logger import get_logger
from versechat_backend.models.chat import ChatRequest, ChatResponse

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from versechat_backend.rag.bible_agent import BibleAgent
        from versechat_backend.rag.tools import bible_search, wiki_tool

        app.state.agent = BibleAgent(
            model_name="openai/gpt-oss-20b", tools=[bible_search, wiki_tool]
        )
    except Exception:
        logger.exception("Bible agent failed to initialize")
        raise

    yield


app = FastAPI(lifespan=lifespan)

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
async def stream_message(request: ChatRequest):
    agent = app.state.agent

    async def generate():
        async for token in agent.stream(request.query):
            yield token

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


@app.post("/ask", response_model=ChatResponse)
async def ask_agent(request: ChatRequest):
    agent = app.state.agent

    try:
        answer, sources = await agent.ask(request.query)

    except Exception:
        logger.exception("failed to serve user request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal error occured",
        )

    return ChatResponse(
        id=uuid.uuid4(), role="assistant", content=answer, sources=sources
    )
