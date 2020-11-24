import pandas as pd
from h2o_wave import app, Q, ui, main
from plotly import graph_objects as go

from .predictor import Predictor
from .config import Configuration
from .plots import (
    convert_plot_to_html,
    generate_figure_pie_of_target_percent,
    get_image_from_matplotlib,
    tall_stat_card_dollars,
    wide_stat_card_dollars,
)

config = Configuration()
predictor = Predictor()


def show_customer_page(q: Q):
    del q.page["content"]
    selected_row = q.args.risk_table[0]
    q.client.selected_customer_id = predictor.get_testing_data_as_pd_frame()["ID"][selected_row]
    score = predictor.predicted_df.as_data_frame().loc[[selected_row]].values[0][0]
    df = predictor.get_testing_data_as_pd_frame()
    df_selected = df.loc[[selected_row]]

    q.page["risk_table_row"] = ui.form_card(box=config.boxes["risk_table_selected"], items=[
        ui.table(
            name='risk_table_row',
            columns=get_column_headers_for_df(df_selected, False),
            rows=get_selected_row(q, df_selected),
            groupable=False,
            resettable=False,
            multiple=False,
        )
    ])


    shap_plot = predictor.get_shap_explanation(selected_row)
    q.page["shap_plot"] = ui.image_card(
        box=config.boxes["shap_plot"],
        title="",
        type="png",
        image=get_image_from_matplotlib(shap_plot),
    )

    q.page["buttons"] = ui.form_card(
        box=config.boxes["button_group"],
        items=[
            ui.buttons([
                ui.button(name='reject_btn', label='Reject', primary=bool(score < config.approval_threshold)),
                ui.button(name='approve_btn', label='Approve', primary=bool(score >= config.approval_threshold)),
            ])
        ]
    )

    # return items


def get_column_headers_for_df(df,searchable):
    columns = [
        ui.table_column(name=column, label=column, sortable=True, searchable=searchable, max_width='300')
        for column in df.columns
    ]
    columns += [ui.table_column(name='approved', label='Approved', cell_type=ui.icon_table_cell_type())]

    return columns


def get_rows(q: Q, df):
    df = df.head(20)
    rows = [
        ui.table_row(
            name=index,
            cells=[str(row[column]) for column in df.columns] + [q.app.customer_status.get(row["ID"]) or '']
        )
        for index, row in df.iterrows()
    ]
    return rows

def get_selected_row(q: Q, df):
    rows = [
        ui.table_row(
            name=index,
            cells=[str(row[column]) for column in df.columns] + [q.app.customer_status.get(row["ID"]) or '']
        )
        for index, row in df.iterrows()
    ]
    return rows


def load_home(q: Q):
    del q.page["content"]
    df = predictor.get_testing_data_as_pd_frame()

    q.page["risk_table"] = ui.form_card(box=config.boxes["risk_table"], items=[
        ui.table(
            name='risk_table',
            columns=get_column_headers_for_df(df, True),
            rows=get_rows(q, df),
            groupable=True,
            resettable=True,
            multiple=False,
        )
    ])


def populate_churn_plots(q):
    shap_plot = predictor.get_shap_explanation(q.client.selected_customer_index)
    q.page["shap_plot"] = ui.image_card(
        box=config.boxes["shap_plot"],
        title="",
        type="png",
        image=get_image_from_matplotlib(shap_plot),
    )

    top_negative_pd_plot = predictor.get_top_negative_pd_explanation(
        q.client.selected_customer_index
    )
    q.page["top_negative_pd_plot"] = ui.image_card(
        box=config.boxes["top_negative_pd_plot"],
        title="Feature Most Contributing to Retention",
        type="png",
        image=get_image_from_matplotlib(top_negative_pd_plot),
    )

    top_positive_pd_plot = predictor.get_top_positive_pd_explanation(
        q.client.selected_customer_index
    )
    q.page["top_positive_pd_plot"] = ui.image_card(
        box=config.boxes["top_positive_pd_plot"],
        title="Feature Most Contributing to Churn",
        type="png",
        image=get_image_from_matplotlib(top_positive_pd_plot),
    )


def get_figure_layout():
    return go.Layout(
        margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0, autoexpand=True)
    )


async def initialize_page(q: Q):
    content = []

    if not q.client.app_initialized:
        # Initialize H2O-3 model and tests data set
        predictor.build_model(config.training_data_url, config.default_model)
        predictor.set_testing_data_frame(config.testing_data_url)
        predictor.predict()

        (q.app.header_png,) = await q.site.upload([config.image_path])
        q.args.menu = "home"
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

    q.page["content"] = ui.form_card(box=config.boxes["content"], items=content)


@app("/")
async def serve(q: Q):
    await initialize_page(q)
    content = q.page["content"]

    if q.args.risk_table:
        show_customer_page(q)
    elif q.args.approve_btn:
        customer_status = q.app.customer_status
        customer_status[q.client.selected_customer_id] = 'BoxCheckmarkSolid'
        load_home(q)
    elif q.args.reject_btn:
        customer_status = q.app.customer_status
        customer_status[q.client.selected_customer_id] = 'BoxMultiplySolid'
        load_home(q)
    else:
        load_home(q)

    await q.page.save()
