from h2o_wave import main, app, Q, ui
import json

from .config import Configuration
from .utils.word_cloud_utils import plot_word_cloud, merge_to_single_text
from .utils.data_utils import filter_data_frame

config = Configuration()


def render_home(q: Q):
    q.page["left_panel"] = ui.form_card(box=config.boxes['left_panel'], items=[
        ui.text_xl("Hotel Reviews"),
        ui.dropdown(
            name="reviews",
            label="Select field",
            placeholder=config.column_mapping[q.client.review] if q.client.review else "please select a review type",
            choices=[
                ui.choice(name=column, label=config.column_mapping[column])
                for column in config.dataset[config.review_column_list]
            ],
            tooltip="Please select the rating option to analyse",
            trigger=True,
        ),
    ])


def populate_dropdown_list(q: Q):
    filter_choices = [
        ui.choice(
            name=json.dumps({"id": q.client.count + 1, "attr": column, "attr_val": None}),
            label=config.column_mapping[column]
        ) for column in config.filterable_columns
    ]
    items = [
        ui.text_l("Filter reviews"),
    ]

    for key, value in q.client.filters.items():
        for attr, attr_val in value.items():
            items.append(ui.dropdown(
                name="filter",
                label="Select filter",
                placeholder=attr,
                choices=[
                    ui.choice(
                        name=json.dumps({'id': key, 'attr': column, 'attr_val': None}),
                        label=config.column_mapping[column]
                    ) for column in config.filterable_columns
                ],
                tooltip="Please select a category to filter",
                trigger=True,
            ), )
            items.append(ui.dropdown(
                name="filter_value",
                label="Select a value",
                placeholder=attr_val,
                choices=[ui.choice(name=json.dumps({'id': key, 'attr': attr, 'attr_val': column}), label=column) for
                         column in config.dataset[attr].drop_duplicates()],
                tooltip="Please select a value to filter",
                trigger=True,
            ), )
            items.append(ui.separator())

    if (q.args.add_filter and all(q.client.filters.values())) or q.args.reviews or q.args.reset_filters:
        items.append(ui.dropdown(
            name="filter",
            label="Select filter",
            placeholder="Please select a category to filter",
            choices=filter_choices,
            tooltip="Please select a category to filter",
            trigger=True
        ), )

    items.append(ui.button(name="compare_review_button", label="Compare Reviews", primary=True))

    return items


def render_filter_toolbar(q):
    render_home(q)

    q.page["filter_toolbar"] = ui.toolbar_card(
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
    )

    filter_dropdown = populate_dropdown_list(q)

    q.page["filters"] = ui.form_card(box=config.boxes['filters'], items=filter_dropdown)


def render_all_text_word_cloud(q: Q):
    image = plot_word_cloud(merge_to_single_text(config.dataset[q.client.review]))

    q.page['all'] = ui.image_card(
        box=config.boxes['middle_panel'],
        title='All',
        type='png',
        image=image,
    )


def render_compare_word_cloud(q: Q):
    df = filter_data_frame(config.dataset, q.client.filters)

    if len(df):
        image = plot_word_cloud(merge_to_single_text(df[q.client.review]))

        q.page['compare'] = ui.image_card(
            box=config.boxes['right_panel'],
            title='Compare',
            type='png',
            image=image,
        )
    else:
        q.page['compare'] = ui.form_card(
            box=config.boxes['right_panel'],
            items=[
                ui.message_bar(type='warning', text='No reviews matching filter criteria!')
            ]
        )


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
    await init(q)
    if q.args.reviews:
        q.client.count = 0
        q.client.review = q.args.reviews
        q.client.filters = {}
        render_filter_toolbar(q)
    elif q.args.add_filter:
        q.client.count = q.client.count + 1
        if not q.client.filters:
            q.client.filters = {}
        if q.args.filter:
            q.client.filters[q.args.filter] = None
        render_filter_toolbar(q)
    elif q.args.filter_value:
        q.args.filter_value = json.loads(q.args.filter_value)
        q.client.filters[q.args.filter_value['id']] = {q.args.filter_value['attr']: q.args.filter_value['attr_val']}
        render_filter_toolbar(q)
    elif q.args.filter:
        q.args.filter = json.loads(q.args.filter)
        q.client.filters[q.args.filter['id']] = {q.args.filter['attr']: q.args.filter['attr_val']}
        render_filter_toolbar(q)
    elif q.args.reset_filters:
        q.client.count = 0
        q.client.filters = {}
        render_filter_toolbar(q)
    elif q.args.compare_review_button:
        render_filter_toolbar(q)

        render_all_text_word_cloud(q)
        render_compare_word_cloud(q)
    else:
        render_home(q)
    await q.page.save()
