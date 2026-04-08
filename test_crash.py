import asyncio
from httpx import AsyncClient
import sys

async def main():
    async with AsyncClient() as client:
        res = await client.post("http://localhost:8000/api/chat", json={
            "user_input": "I am so sad right now",
            "history": [
                {"role": "user", "content": "hello", "display_content": None},
                {"role": "assistant", "content": "hi", "display_content": None}
            ]
        }, timeout=30)
        print(res.text)

asyncio.run(main())
