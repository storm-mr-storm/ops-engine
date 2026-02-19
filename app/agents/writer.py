import json
from app.db import AsyncSessionLocal
from app.models import Run
from sqlalchemy import select
from app.bus import publish

async def handle_writer(message):
    event_type = message["type"]

    if event_type != "brief.created":
        return

    payload = json.loads(message["data"])
    run_id = payload["run_id"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one()

        # Stub prompt generation
        generated_prompt = f"{run.character} exploring a magical garden at golden hour"

        run.prompt = generated_prompt
        run.status = "PROMPT_READY"

        await session.commit()

    await publish("prompt.ready", {"run_id": run_id})
    print("Writer completed for:", run_id)
