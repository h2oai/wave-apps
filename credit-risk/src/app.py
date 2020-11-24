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
    training_df = predictor.get_testing_data_as_pd_frame()
    predictions_df = predictor.predicted_df.as_data_frame()
    contributions_df = predictor.contributions_df.as_data_frame()
    del contributions_df['BiasTerm']

    q.client.selected_customer_id = training_df.loc[selected_row]["ID"]
    score = predictions_df.loc[selected_row]["predict"]

    approve = bool(score >= config.approval_threshold)

    q.page["risk_table_row"] = ui.form_card(box=config.boxes["risk_table_selected"], items=[
        ui.table(
            name='risk_table_row',

            columns=[
                ui.table_column(name="Attribute", label="Attribute", sortable=False, searchable=False, max_width='100'),
                ui.table_column(name="Value", label="Value", sortable=False, searchable=False, max_width='100')
            ],
            rows=get_transformed_df_rows(q, training_df.loc[[selected_row]]),
            groupable=False,
            resettable=False,
            multiple=False,
            height='100%'
        )
    ])

    shap_plot = predictor.get_shap_explanation(selected_row)
    q.page["shap_plot"] = ui.image_card(
        box=config.boxes["shap_plot"],
        title="",
        type="png",
        image=get_image_from_matplotlib(shap_plot, figsize=(8, 6), dpi=85),
    )

    top_feature = \
        contributions_df.idxmax(axis=1)[selected_row] if approve else contributions_df.idxmin(axis=1)[selected_row]

    explanation_data = {
        'will_or_will_not': 'will' if approve else 'will not',
        'top_contributing_feature': top_feature,
        'value_of_top_contributing_feature': str(training_df.loc[selected_row][top_feature]),
        'accept_or_reject': 'accept' if approve else 'reject',
    }

    explanation = '''
- This customer **{{will_or_will_not}}** most probably settle the next month credit card balance.
- Having a {{top_contributing_feature}} of {{value_of_top_contributing_feature}} is the top reason for that.
- It's a good idea to **{{accept_or_reject}}** this customer. 
'''

    q.page["risk_explanation"] = ui.markdown_card(
        box=config.boxes["risk_explanation"],
        title='Summary on Customer',
        content='=' + explanation,
        data=explanation_data,
    )

    q.page["buttons"] = ui.form_card(
        box=config.boxes["button_group"],
        items=[
            ui.buttons([
                ui.button(name='reject_btn', label='Reject', primary=not approve),
                ui.button(name='approve_btn', label='Approve', primary=approve),
            ])
        ]
    )


def get_column_headers_for_df(df, searchable):
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


def get_transformed_df_rows(q: Q, df):
    df_transformed = df.transpose()

    rows = [
        ui.table_row(
            name=index,
            cells=[str(index)] + [str(row[column]) for column in df_transformed.columns]
        )
        for index, row in df_transformed.iterrows()
    ]
    rows += [ui.table_row(
        name='approved',
        cells=['Approved'] + [q.app.customer_status.get(q.client.selected_customer_id) or 'Pending'])]
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
