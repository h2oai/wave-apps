from h2o_wave import app, Q, ui, main

from .views.home import render_home
from .views.customer import render_customer_page, handle_approve_click, handle_reject_click


def init(q: Q):
    q.app.customer_status = {}


@app("/")
async def serve(q: Q):
    if not q.app.initialized:
        init(q)
        q.app.initialized = True

    if q.args.risk_table:
        render_customer_page(q)
    elif q.args.approve_btn:
        handle_approve_click(q)
        render_home(q)
    elif q.args.reject_btn:
        handle_reject_click(q)
        render_home(q)
    else:
        render_home(q)

    await q.page.save()
