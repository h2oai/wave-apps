from h2o_wave import app, Q, ui, main

from .views.home import load_home
from .views.customer import show_customer_page, handle_approve_click, handle_reject_click


def init(q: Q):
    q.app.customer_status = {}


@app("/")
async def serve(q: Q):
    if not q.app.initialized:
        init(q)
        q.app.initialized = True

    if q.args.risk_table:
        show_customer_page(q)
    elif q.args.approve_btn:
        handle_approve_click(q)
        load_home(q)
    elif q.args.reject_btn:
        handle_reject_click(q)
        load_home(q)
    else:
        load_home(q)

    await q.page.save()
