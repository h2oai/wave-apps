import pytest

from tested_app.workers import calculate_sum
from tests.unit_tests.utils import on_done_pass, on_update_pass


@pytest.mark.asyncio
@pytest.mark.parametrize("input, expected", [(1, 1), (2, 3), (3, 6), (4, 10)])
async def test_sum_result(input: int, expected: int):
    calc_result = ""

    async def on_done(result: str):
        nonlocal calc_result
        calc_result = result

    await calculate_sum(input, on_update=on_update_pass, on_done=on_done, sleep=0.0001)
    assert calc_result == str(expected)


@pytest.mark.asyncio
async def test_cancel_sum():
    updates = 3

    async def on_update(update: float) -> bool:
        nonlocal updates
        updates -= 1
        return updates == 0

    await calculate_sum(5, on_update=on_update, on_done=on_done_pass, sleep=0.0001)
    assert updates == 0, "on_update is not called after cancelling"


@pytest.mark.asyncio
@pytest.mark.parametrize("input", [(1), (2), (3)])
async def test_updates_called(input):
    updates = 0

    async def on_update(update: float) -> bool:
        nonlocal updates
        updates += 1
        return False

    await calculate_sum(input, on_update=on_update, on_done=on_done_pass, sleep=0.0001)
    assert updates == input
