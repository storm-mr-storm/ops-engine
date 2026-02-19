import os
import redis.asyncio as redis
import json

REDIS_URL = os.getenv("REDIS_URL")

r = redis.from_url(REDIS_URL, decode_responses=True)

STREAM_NAME = "ops_events"

async def publish(event_type: str, payload: dict):
    event = {
        "type": event_type,
        "data": json.dumps(payload)
    }
    await r.xadd(STREAM_NAME, event)

async def consume(handler):
    last_id = "0-0"
    while True:
        response = await r.xread({STREAM_NAME: last_id}, block=5000, count=1)
        if response:
            stream, messages = response[0]
            for message_id, message in messages:
                last_id = message_id
                await handler(message)
