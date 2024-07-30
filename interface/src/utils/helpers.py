# utils/helpers.py
import asyncio
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent.parent

def run_async(coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)