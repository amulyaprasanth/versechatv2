from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from versechat_backend.core.logger import get_logger
from versechat_backend.models.chat import ChatRequest, ChatResponse

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from versechat_backend.rag.bible_agent import BibleAgent
        from versechat_backend.rag.tools import bible_search, wiki_tool

        app.state.agent = BibleAgent(
            model_name="llama-3.3-70b-versatile", tools=[bible_search, wiki_tool]
        )
    except Exception:
        logger.exception("Bible agent failed to initialize")
        raise

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health", status_code=200)
async def get_health():
    return JSONResponse({"message": "healthy"})


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

    return ChatResponse(answer=answer, sources=sources)
