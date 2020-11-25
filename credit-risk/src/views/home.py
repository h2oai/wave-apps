from h2o_wave import Q, ui

from ..config import config, predictor


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


def load_home(q: Q):
    df = predictor.get_testing_data_as_pd_frame()

    q.page["risk_table"] = ui.form_card(box=config.boxes["risk_table"], items=[
        ui.table(
            name='risk_table',
            columns=get_column_headers_for_df(df, True),
            rows=get_rows(q, df),
            groupable=True,
            resettable=True,
            multiple=False,
            tooltip='Double click a row to go to select it.'
        )
    ])