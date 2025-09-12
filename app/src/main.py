from fastapi import FastAPI
from src.finances.routes import router as finanses_router


app = FastAPI()


@app.get("/ping")
async def ping_pong():
    return {"message": "pong"}


app.include_router(finanses_router)
