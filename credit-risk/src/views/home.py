from h2o_wave import Q, ui

from .header import render_header
from ..config import predictor
from ..utils import add_column_to_df, drop_column_from_df, round_df_column


def init(q: Q):
    q.page.drop()
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone('title', size='80px'),
                ui.zone('menu', size='80px'),
                ui.zone('risk_table'),
            ]
        ),
        ui.layout(
            breakpoint='m',
            width='1920px',
            zones=[
                ui.zone('header', size='80px', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('title', size='400px'),
                    ui.zone('menu'),
                ]),
                ui.zone('risk_table', direction=ui.ZoneDirection.ROW, size='800px'),
            ]
        )
    ])

    render_header(q)


def get_column_headers_for_df(df, searchable):
    columns = [
        ui.table_column(name=column, label=column, sortable=True, searchable=searchable, max_width='300')
        for column in df.columns
    ]
    columns += [ui.table_column(name='status', label='Status', cell_type=ui.icon_table_cell_type())]

    return columns


def get_rows(q: Q, df):
    df = df.head(20)
    rows = [
        ui.table_row(
            name=str(index),
            cells=[str(row[column]) for column in df.columns] + [q.app.customer_status.get(row["ID"]) or '']
        )
        for index, row in df.iterrows()
    ]
    return rows


def render_home(q: Q):
    init(q)

    df = predictor.get_testing_data_as_pd_frame()
    predicted_df = predictor.get_predict_data_as_pd_frame()
    drop_column_from_df(df, 'default.payment.next.month')
    add_column_to_df(df, predicted_df, 'Default Prediction Rate', 'predict')
    df = round_df_column(df, 'Default Prediction Rate', 4)

    q.page["risk_table"] = ui.form_card(
        box='risk_table',
        items=[
            ui.message_bar(text='Double click to review a customer', type='info'),
            ui.table(
                name='risk_table',
                columns=get_column_headers_for_df(df, True),
                rows=get_rows(q, df),
                groupable=True,
                multiple=False,
                height="800px"
            )
        ]
    )
