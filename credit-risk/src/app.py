from h2o_wave import app, Q, ui, main

from .config import config
from .views.home import load_home
from .views.customer import show_customer_page, handle_approve_click, handle_reject_click


async def init(q: Q):
    if not q.app.initialized:
        (q.app.header_png,) = await q.site.upload([config.image_path])
        q.app.customer_status = {}
        q.app.initialized = True

    q.page.drop()

    q.page["title"] = ui.header_card(
        box=config.boxes["banner"],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page["navbar"] = ui.breadcrumbs_card(
        box=config.boxes["navbar"],
        items=[
            ui.breadcrumb(name='home', label='Home'),
        ],
    )


@app("/")
async def serve(q: Q):
    await init(q)

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
