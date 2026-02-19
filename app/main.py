from fastapi import FastAPI
import asyncio
import json
from uuid import uuid4

from sqlalchemy import select

from app.db import engine, AsyncSessionLocal
from app.models import Base, Run
from app.bus import publish, consume
from app.agents.writer import handle_writer
from app.agents.producer import handle_producer

app = FastAPI()


@app.on_event("startup")
async def startup():
    import asyncio
    import asyncpg
    import os

    DATABASE_URL = os.getenv("DATABASE_URL")

    # Retry loop for DB readiness
    for attempt in range(10):
        try:
            conn = await asyncpg.connect(DATABASE_URL.replace("+asyncpg", ""))
            await conn.close()
            break
        except Exception:
            print("Waiting for Postgres...")
            await asyncio.sleep(2)
    else:
        raise Exception("Could not connect to Postgres.")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Event router
    async def router(message):
        await handle_writer(message)
        await handle_producer(message)

    asyncio.create_task(consume(router))



@app.get("/")
async def root():
    return {"status": "Ops Engine running"}


@app.post("/test-event")
async def test_event():
    await publish("test.created", {"hello": "world"})
    return {"status": "event published"}


@app.post("/runs")
async def create_run(character: str):
    async with AsyncSessionLocal() as session:
        run = Run(character=character, status="CREATED")
        session.add(run)
        await session.commit()
        await session.refresh(run)

    await publish("brief.created", {"run_id": str(run.id)})

    return {"run_id": str(run.id)}
