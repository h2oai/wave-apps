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
            name="review_choice",
            label="Choose a review type",
            placeholder=config.column_mapping[q.client.review] if q.client.review else "please select a review type",
            choices=[
                ui.choice(name=column, label=config.column_mapping[column])
                for column in config.dataset[config.review_column_list]
            ],
            trigger=True,
        ),
    ])


def populate_dropdown_list(q: Q):
    filter_choices = [
        ui.choice(
            name=json.dumps({"id": q.client.filter_count + 1, "attr": column, "attr_val": None}),
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
                label="Choose a review attribute",
                placeholder=config.column_mapping[attr],
                choices=[
                    ui.choice(
                        name=json.dumps({'id': key, 'attr': column, 'attr_val': None}),
                        label=config.column_mapping[column]
                    ) for column in config.filterable_columns
                ],
                trigger=True,
            ), )
            items.append(ui.dropdown(
                name="filter_value",
                label="Choose a value for selected review attribute",
                placeholder=attr_val,
                choices=[ui.choice(name=json.dumps({'id': key, 'attr': attr, 'attr_val': column}), label=column) for
                         column in config.dataset[attr].drop_duplicates()],
                trigger=True,
            ), )
            items.append(ui.separator())

    if (q.args.add_filter and all(q.client.filters.values())) or q.args.review_choice or q.args.reset_filters:
        items.append(ui.dropdown(
            name="filter",
            label="Choose a review attribute",
            placeholder="Please select a category to filter",
            choices=filter_choices,
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


def get_text_word_cloud_plot(q: Q):
    return plot_word_cloud(merge_to_single_text(config.dataset[q.client.review]))


def render_text_word_cloud_image(q: Q, image):
    q.page['all'] = ui.image_card(
        box=config.boxes['middle_panel'],
        title=f'Word Cloud of the {config.column_mapping[q.client.review]}',
        type='png',
        image=image,
    )


def render_all_text_word_cloud(q: Q):
    image = plot_word_cloud(merge_to_single_text(config.dataset[q.client.review]))

    q.page['all'] = ui.image_card(
        box=config.boxes['middle_panel'],
        title=f'Word Cloud of the {config.column_mapping[q.client.review]}',
        type='png',
        image=image,
    )


def render_compare_word_cloud(q: Q):
    df = filter_data_frame(config.dataset, q.client.filters)

    if len(df):
        image = plot_word_cloud(merge_to_single_text(df[q.client.review]))

        q.page['compare'] = ui.image_card(
            box=config.boxes['right_panel'],
            title='Word Cloud based on the selected filters',
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
        reset_filters(q)
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


def reset_filters(q: Q):
    q.client.filter_count = 0
    q.client.filters = {}


@app("/")
async def serve(q: Q):
    await init(q)
    if q.args.review_choice:
        q.client.review = q.args.review_choice
        render_filter_toolbar(q)
        q.client.all_text_word_cloud = get_text_word_cloud_plot(q)
        render_text_word_cloud_image(q, q.client.all_text_word_cloud)
    elif q.args.add_filter:
        q.client.filter_count += 1
        if not q.client.filters:
            q.client.filters = {}
        if q.args.filter:
            q.client.filters[q.args.filter] = None
        render_filter_toolbar(q)
        render_text_word_cloud_image(q, q.client.all_text_word_cloud)
    elif q.args.filter_value:
        q.args.filter_value = json.loads(q.args.filter_value)
        q.client.filters[q.args.filter_value['id']] = {q.args.filter_value['attr']: q.args.filter_value['attr_val']}
        render_filter_toolbar(q)
        render_text_word_cloud_image(q, q.client.all_text_word_cloud)
    elif q.args.filter:
        q.args.filter = json.loads(q.args.filter)
        q.client.filters[q.args.filter['id']] = {q.args.filter['attr']: q.args.filter['attr_val']}
        render_filter_toolbar(q)
        render_text_word_cloud_image(q, q.client.all_text_word_cloud)
    elif q.args.reset_filters:
        reset_filters(q)
        render_filter_toolbar(q)
        render_all_text_word_cloud(q)
    elif q.args.compare_review_button:
        render_filter_toolbar(q)

        render_text_word_cloud_image(q, q.client.all_text_word_cloud)
        render_compare_word_cloud(q)
    else:
        render_home(q)
    await q.page.save()
