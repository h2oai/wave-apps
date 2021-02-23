import asyncio
from types import SimpleNamespace


def async_stub() -> asyncio.Future:
    f = asyncio.Future()
    f.set_result(None)
    return f


async def on_done_pass(result: str):
    pass


async def on_update_pass(update: float) -> bool:
    return False


def Q(**kwargs) -> SimpleNamespace:
    return SimpleNamespace(app=SimpleNamespace(), args=SimpleNamespace(**kwargs))
