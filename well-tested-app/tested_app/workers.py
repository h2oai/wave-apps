import time
from typing import Awaitable, Callable


async def calculate_sum(
    number: int,
    on_update: Callable[[float], Awaitable[bool]],
    sleep: float = 1,
):
    result = 0
    for i in range(1, number + 1):
        time.sleep(sleep)
        result += i
        if await on_update(i / number):
            return "Stopped"
    return str(result)


async def calculate_factorial(
    number: int,
    on_update: Callable[[float], Awaitable[bool]],
    sleep: float = 1,
):
    result = 1
    for i in range(1, number + 1):
        time.sleep(sleep)
        result *= i
        if await on_update(i / number):
            return "Stopped"
    return str(result)
