import pytest
from pytest_mock import MockerFixture

from tested_app.app import do_calculate
from tests.unit_tests.utils import Q, async_stub


@pytest.mark.parametrize(
    "function, number, expected",
    [("sum", 2, 3), ("sum", 5, 15), ("factorial", 4, 24), ("factorial", 10, 3628800)],
)
@pytest.mark.asyncio
async def test_do_calculate(
    function: str, number: int, expected: int, mocker: MockerFixture
):
    q = Q(function=function, number=[number, 10])
    render = mocker.patch("tested_app.app.render_calculate", return_value=async_stub())
    mocker.patch("time.sleep")
    mocker.patch("tested_app.workers.time.sleep")
    await do_calculate(q)  # type: ignore
    assert q.app.result == str(expected)
    assert render.call_count == number + 2
