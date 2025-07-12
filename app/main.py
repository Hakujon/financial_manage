from fastapi import FastAPI
from app.finances.routes import router as expense_router


app = FastAPI()


@app.get("/ping")
async def ping_pong():
    return {"message": "pong"}


app.include_router(expense_router)
