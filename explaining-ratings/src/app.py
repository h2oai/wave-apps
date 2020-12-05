from h2o_wave import main, app, Q, ui

from .config import Configuration
from .visualizer import plot_word_cloud
from .utils import merge_to_single_text

config = Configuration()


def home_content(q: Q):
    q.page["left_panel"] = ui.form_card(box=config.boxes['left_panel'], items=[
        ui.text_xl("Choose a category"),
        ui.dropdown(
            name="reviews",
            label="Hotel Reviews",
            placeholder=q.client.review if q.client.review else "please select a review type",
            choices=[ui.choice(name=column, label=column) for column in config.dataset[config.review_column_list]],
            tooltip="Please select the rating option to analyse",
            trigger=True,
        ),
    ])


def populate_dropdown_list(q: Q):
    print(q.args)
    filter_choices = [
        ui.choice(name=column, label=column) for column in config.dataset.columns
    ]
    items = [
        ui.text_l("Select a sub category"),
    ]

    for filter in q.client.filters:
        items.append(ui.dropdown(
            name="filter",
            label="Select filter",
            placeholder=filter,
            choices=filter_choices,
            tooltip="Please select a category to filter",
        ), )

    if not q.args.filter or q.args.add_filter or q.args.reviews or q.args.reset_filter:
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
    home_content(q)

    q.page.add("filter_toolbar", ui.toolbar_card(
        box=config.boxes["new_filter"],
        items=[
            ui.command(
                name='add_filter',
                label='Add filter',
                caption='Create a new filter',
                icon='Add',
            ),
            ui.command(
                name='reset_filters',
                label='Reset filters',
                caption='Reset the filters',
                icon='Delete',
            )
        ]
    ))

    filter_dropdown = populate_dropdown_list(q)

    q.page["filters"] = ui.form_card(box=config.boxes['filters'], items=filter_dropdown)


async def init(q: Q):
    if not q.client.app_initialized:
        (q.app.header_png,) = await q.site.upload([config.image_path])
        (q.app.training_file_url,) = await q.site.upload([config.training_path])
        config.init_dataset()
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
    print(q.args)
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
    elif q.args.reset_filters:
        q.client.filters = set()
        add_filters(q)
    elif q.args.compare_review_button:
        if q.args.filter:
            q.client.filters.add(q.args.filter)
            add_filters(q)

        image = plot_word_cloud(merge_to_single_text(config.dataset['reviews.text']))

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
