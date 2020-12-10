from h2o_wave import app, Q, ui, main

from .config import config
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
        # TODO: This is a temporary solution until spinner component available.
        #  https://github.com/h2oai/wave/issues/323
        # q.page["loading_predictions"] = ui.form_card(box="1 2 -1 -1", items=[ui.progress(label="Loading predictions")])
        # await q.page.save()
        show_customer_page(q)
        # del q.page["loading_predictions"]
    elif q.args.approve_btn:
        handle_approve_click(q)
        load_home(q)
    elif q.args.reject_btn:
        handle_reject_click(q)
        load_home(q)
    else:
        load_home(q)

    await q.page.save()
