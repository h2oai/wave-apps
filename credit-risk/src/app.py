from h2o_wave import app, Q, ui, main

from .config import config, predictor
from .views.home import load_home
from .views.customer import show_customer_page, handle_approve_click, handle_reject_click


async def init(q: Q):
    if not q.client.app_initialized:
        # Initialize H2O-3 model and tests data set
        predictor.build_model(config.training_data_url, config.default_model)
        predictor.set_testing_data_frame(config.testing_data_url)
        predictor.predict()

        (q.app.header_png,) = await q.site.upload([config.image_path])
        q.app.customer_status = {}
        q.client.app_initialized = True

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
