from h2o_wave import main, app, Q, ui
import pandas as pd

from .config import Configuration
from .visualizer import plot_word_cloud
from .utils import merge_to_single_text

config = Configuration()


def home_content(q: Q):
    df = config.get_dataset()

    choices = [
        ui.choice(name=column, label=column) for column in df[config.review_column_list]
    ]
    items = [
        ui.text_xl("Choose a category"),
        ui.dropdown(
            name="reviews",
            label="Hotel Reviews",
            placeholder="please select a review type",
            choices=choices,
            tooltip="Please select the rating option to analyse",
            trigger=True,
        ),
    ]

    q.page["left_panel"] = ui.form_card(box=config.boxes['left_panel'], items=items)


def populate_dropdown_list(q: Q, filter_choices):
    print(q.client.filters)
    items = [
        ui.text_l("Select a sub category"),
    ]

    if not q.client.filters:
        items.append(ui.dropdown(
            name="filter",
            label="Select filter",
            placeholder="Please select a category to filter",
            choices=filter_choices,
            tooltip="Please select a category to filter",
        ), )
    else:
        for filter in q.client.filters:
            items.append(ui.dropdown(
                name="filter",
                label="Select filter",
                placeholder=filter,
                choices=filter_choices,
                tooltip="Please select a category to filter",
            ), )
        items.append(ui.dropdown(
            name="filter",
            label="Select filter",
            placeholder="Please select a category to filter",
            choices=filter_choices,
            tooltip="Please select a category to filter",
        ), )

    items.append(ui.button(name="compare_review_button", label="Compare Reviews", primary=True))

    return items


def add_filters(q):
    df = pd.read_csv(config.training_path).head(40)

    choices = [
        ui.choice(name=column, label=column) for column in df[config.review_column_list]
    ]
    items = [
        ui.text_l("Choose a category"),
        ui.dropdown(
            name="reviews",
            label="Hotel Reviews",
            placeholder=q.client.review,
            choices=choices,
            tooltip="Please select the rating option to analyse",
            trigger=True,
        ),
    ]

    q.page["left_panel"] = ui.form_card(box=config.boxes['left_panel'], items=items)
    q.page.add("filters", ui.toolbar_card(
        box=config.boxes["new_filter"],
        items=[
            ui.command(
                name='add_filter',
                label='New filter',
                caption='Create a new filter',
                icon='Add',
            )
        ]
    ))

    filter_choices = [
        ui.choice(name=column, label=column) for column in df.columns
    ]

    filter_dropdown = populate_dropdown_list(q, filter_choices)

    q.page["filters_one"] = ui.form_card(box=config.boxes['filters'], items=filter_dropdown)


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
    if q.args.reviews:
        q.client.review = q.args.reviews
        q.client.filters = set()
        add_filters(q)
    elif q.args.add_filter:
        if not q.client.filters:
            q.client.filters = set()
        if q.args.filter:
            q.client.filters.add(q.args.filter)
        add_filters(q)
    elif q.args.compare_review_button:
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
    else:
        home_content(q)
    await q.page.save()
