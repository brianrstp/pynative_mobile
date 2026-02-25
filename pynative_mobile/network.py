from .state import State
import httpx
import asyncio
from typing import Any


async def _fetch_json(url: str, state: State) -> None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data: Any = resp.json()
            state.value = data
    except Exception as exc:
        state.value = exc

def fetch(url: str) -> State:
    state = State(None)
    async def runner():
        await _fetch_json(url, state)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(runner())
    except RuntimeError:
        import threading
        def _thread_target():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(runner())
        thread = threading.Thread(target=_thread_target, daemon=True)
        thread.start()
    return state