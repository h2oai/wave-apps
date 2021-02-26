import pytest

from tested_app.workers import calculate_factorial
from tests.unit_tests.utils import on_update_pass


@pytest.mark.asyncio
@pytest.mark.parametrize("input, expected", [(1, 1), (2, 2), (3, 6), (4, 24)])
async def test_sum_result(input: int, expected: int):
    assert await calculate_factorial(
        input, on_update=on_update_pass, sleep=0.0001
    ) == str(expected)


@pytest.mark.asyncio
async def test_cancel_sum():
    updates = 3

    async def on_update(update: float) -> bool:
        nonlocal updates
        updates -= 1
        return updates == 0

    await calculate_factorial(5, on_update=on_update, sleep=0.0001)
    assert updates == 0, "on_update is not called after cancelling"


@pytest.mark.asyncio
@pytest.mark.parametrize("input", [(1), (2), (3)])
async def test_updates_called(input):
    updates = 0

    async def on_update(update: float) -> bool:
        nonlocal updates
        updates += 1
        return False

    await calculate_factorial(input, on_update=on_update, sleep=0.0001)
    assert updates == input
