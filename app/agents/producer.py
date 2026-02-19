import json
from app.db import AsyncSessionLocal
from app.models import Run
from sqlalchemy import select

async def handle_producer(message):
    event_type = message["type"]

    if event_type != "prompt.ready":
        return

    payload = json.loads(message["data"])
    run_id = payload["run_id"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one()

        # Simulate video generation
        print("Generating video for prompt:", run.prompt)

        run.status = "GENERATED"

        await session.commit()

    print("Producer completed for:", run_id)
