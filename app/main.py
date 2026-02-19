from fastapi import FastAPI
import asyncio

from app.db import engine
from app.models import Base
from app.bus import publish, consume
from app.agents.logger import handle_event

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start background event consumer
    asyncio.create_task(consume(handle_event))

@app.get("/")
async def root():
    return {"status": "Ops Engine running"}

@app.post("/test-event")
async def test_event():
    await publish("test.created", {"hello": "world"})
    return {"status": "event published"}
