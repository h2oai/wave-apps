from h2o_wave import Q, ui

from .header import render_header
from ..config import config, predictor
from ..plots import get_image_from_matplotlib
from ..utils import add_column_to_df, drop_column_from_df, round_df_column


def get_customer_status(q):
    status = "Pending"
    customer_status = q.app.customer_status.get(q.client.selected_customer_id)
    if customer_status == "BoxCheckmarkSolid":
        status = "Accepted"
    elif customer_status == "BoxMultiplySolid":
        status = "Rejected"
    return status


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
        cells=['Status'] + [get_customer_status(q)])]
    return rows


def render_customer_details_table(q: Q, df, row):
    q.page.add('risk_table_row', ui.form_card(
        box='risk_table_selected',
        items=[
            ui.table(
                name='risk_table_row',
                columns=[
                    ui.table_column(name="attribute", label="Attribute", sortable=False, searchable=False, max_width='100'),
                    ui.table_column(name="value", label="Value", sortable=False, searchable=False, max_width='100')
                ],
                rows=get_transformed_df_rows(q, df.loc[[row]]),
                groupable=False,
                resettable=False,
                multiple=False,
                height='100%'
            )
        ])
   )


def render_customer_summary(q: Q, training_df, contributions_df, row, can_approve):
    top_feature = \
        contributions_df.idxmin(axis=1)[row] if can_approve else contributions_df.idxmax(axis=1)[row]

    explanation_data = {
        'will_or_will_not': 'will' if can_approve else 'will not',
        'top_contributing_feature': top_feature,
        'value_of_top_contributing_feature': str(training_df.loc[row][top_feature]),
        'accept_or_reject': 'approve' if can_approve else 'reject',
    }

    explanation = '''
- This customer **{{will_or_will_not}}** most probably settle the next month credit card balance.
- Having a {{top_contributing_feature}} of {{value_of_top_contributing_feature}} is the top reason for that.
- It's a good idea to **{{accept_or_reject}}** this customer. 
'''

    q.page["risk_explanation"] = ui.markdown_card(
        box='risk_explanation',
        title='Summary on Customer',
        content='=' + explanation,
        data=explanation_data,
    )


def handle_approve_click(q: Q):
    customer_status = q.app.customer_status
    customer_status[q.client.selected_customer_id] = 'BoxCheckmarkSolid'


def handle_reject_click(q: Q):
    customer_status = q.app.customer_status
    customer_status[q.client.selected_customer_id] = 'BoxMultiplySolid'


def show_customer_page(q: Q):
    q.page.drop()
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xl',
            width='1920px',
            zones=[
                ui.zone('header', size='80px', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('title', size='400px'),
                    ui.zone('menu'),
                    ui.zone('button_group', size='200px'),
                ]),
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('risk_table_selected', size='400px'),
                    ui.zone('pane', direction=ui.ZoneDirection.COLUMN, zones=[
                        ui.zone('risk_explanation', size='150px'),
                        ui.zone('shap_plot'),
                    ])
                ]),
            ]
        )
    ])

    render_header(q)

    selected_row = q.args.risk_table[0]
    training_df = predictor.get_testing_data_as_pd_frame()
    predictions_df = predictor.predicted_df.as_data_frame()
    contributions_df = predictor.contributions_df.as_data_frame()
    del contributions_df['BiasTerm']

    q.client.selected_customer_id = training_df.loc[selected_row]["ID"]
    score = predictions_df.loc[selected_row]["predict"]
    approve = bool(score < config.approval_threshold)

    drop_column_from_df(training_df, 'default.payment.next.month')
    add_column_to_df(training_df, predictions_df, 'Default Prediction Rate', 'predict')
    training_df = round_df_column(training_df, 'Default Prediction Rate', 4)

    render_customer_details_table(q, training_df, selected_row)

    shap_plot = predictor.get_shap_explanation(selected_row)
    q.page["shap_plot"] = ui.image_card(
        box='shap_plot',
        title="Effectiveness of each attribute on defaulting next payment",
        type="png",
        image=get_image_from_matplotlib(shap_plot, dpi=85),
    )

    render_customer_summary(q, training_df, contributions_df, selected_row, approve)

    q.page["buttons"] = ui.form_card(
        box='button_group',
        items=[
            ui.buttons([
                ui.button(name='reject_btn', label='Reject', primary=not approve),
                ui.button(name='approve_btn', label='Approve', primary=approve),
            ])
        ]
    )
