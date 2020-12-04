from h2o_wave import main, app, Q, ui

from .config import Configuration
from .visualizer import plot_word_cloud
from .utils import merge_to_single_text

config = Configuration()


def home_content(q: Q):
    df = config.get_dataset()

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

    image = plot_word_cloud(merge_to_single_text(config.get_dataset()['reviews.text']))

    q.page['all'] = ui.image_card(
        box=config.boxes['middle_panel'],
        title='All',
        type='png',
        image=image,
    )

    q.page['compare'] = ui.image_card(
        box=config.boxes['right_panel'],
        title='Compare',
        type='png',
        image=image,
    )

    await q.page.save()
