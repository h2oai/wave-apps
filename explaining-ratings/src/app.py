import pandas as pd
from h2o_wave import app, main, Q, ui

from .config import Configuration

config = Configuration()


def home_content(q: Q):
    df = pd.read_csv(config.training_path).head(40)

    choices = [
        ui.choice(name=column, label=column) for column in df.columns
    ]
    items = [
        ui.text_xl("Choose a category"),
        ui.picker(
            name="reviews",
            label="Hotel Reviews",
            choices=choices,
            max_choices=1,
            tooltip="Start typing to search for a customer",
            trigger=True,
        ),
    ]

    q.page["left_panel"] = ui.form_card(box=config.boxes['left_panel'], items=items)


async def init(q: Q):
    print("init 1")

    if not q.client.app_initialized:
        (q.app.header_png,) = await q.site.upload([config.image_path])
        (q.app.training_file_url,) = await q.site.upload([config.training_path])
        q.client.app_initialized = True

    q.page.drop()

    q.page["title"] = ui.header_card(
        box=config.boxes["banner"],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )


@app("/")
async def serve(q: Q):
    await init(q)
    home_content(q)
    await q.page.save()
