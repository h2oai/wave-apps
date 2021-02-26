from h2o_wave import Q, app, main  # noqa F401

from .views import render_calculate, render_main
from .workers import calculate_factorial, calculate_sum


@app("/")
async def serve(q: Q):
    if q.args.stop:
        await do_stop(q)
    elif q.args.calculate:
        await do_calculate(q)
    else:
        await render_main(q)


async def do_stop(q: Q):
    q.app.result = "Stopped"
    await render_calculate(q)


async def do_calculate(q: Q):
    async def on_update(progress: float):
        q.app.progress = progress
        await render_calculate(q)
        return q.app.result

    q.app.function = q.args.function
    q.app.result = None
    await render_calculate(q)
    if q.app.function == "sum":
        q.app.result = await calculate_sum(q.args.number[0], on_update=on_update)
    else:
        q.app.result = await calculate_factorial(q.args.number[0], on_update=on_update)
    await render_calculate(q)
