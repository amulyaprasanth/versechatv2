from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/health", status_code=200)
async def get_health():
    return JSONResponse({"message": "healthy"})
