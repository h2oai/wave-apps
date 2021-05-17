import pandas as pd
from h2o_wave import app, data, handle_on, main, on, Q, ui

from .model import Model


TRAIN_CSV = "./data/Kaggle/CreditCard-train.csv"
TEST_CSV = "./data/Kaggle/CreditCard-train.csv"
ID_COLUMN = "ID"
TARGET_COLUMN = "default.payment.next.month"
# Recommend rejecting customer's with default probability appove this amount 
APPROVAL_THRESHOLD = 0.35


def init_app(q: Q):
    q.app.initialized = True
    # build model
    q.app.model = Model(TRAIN_CSV, ID_COLUMN, TARGET_COLUMN)
    # prep df for analyzation
    df = pd.read_csv(TEST_CSV).head(20)
    df.drop(TARGET_COLUMN, axis=1, inplace=True)
    # analyze df
    q.app.predictions_df = q.app.model.predict(df)
    q.app.contributions_df = q.app.model.contrib(df)
    # prep df for viewing
    df['Default Prediction Rate'] = q.app.predictions_df.round(4)
    df.insert(loc=0, column='Status', value='Pending', allow_duplicates=True) 
    q.app.customer_df = df


def init_client(q: Q):
    q.client.initialized = True
    q.page['meta'] = ui.meta_card(
        box='', 
        title='Credit Risk', 
        layouts=[
            ui.layout(
                breakpoint='xs',
                zones=[
                    ui.zone('header'),
                    ui.zone('customer_table'),
                    ui.zone(
                        'customer_page',
                        zones=[
                            ui.zone('customer_risk_explanation'),
                            ui.zone('customer_shap_plot', size='600px'),
                            ui.zone('button_group'),
                            ui.zone('customer_features'),
                        ]
                    )
                ]
            ),
            ui.layout(
                breakpoint='m',
                zones=[
                    ui.zone('header'),
                    ui.zone('customer_table'),
                    ui.zone(
                        'customer_page',
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone(
                                'content',
                                zones=[
                                    ui.zone('customer_risk_explanation'),
                                    ui.zone('customer_shap_plot'), size='600px'),
                                    ui.zone('button_group'),
                                ]
                            ),
                            ui.zone('customer_features', size='300px'),
                        ]
                    )
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='Credit Card Risk',
        subtitle='Review customer ability to pay credit card bills',
        icon='PaymentCard',
        nav=[
            ui.nav_group(
                'Navigation', 
                items=[
                    ui.nav_item(name='render_customer_selector', label='Customers'),
                ]
            ),
            ui.nav_group(
                'Options', 
                items=[
                    ui.nav_item(name='dark_mode', label='Dark Mode'),
                    ui.nav_item(name='light_mode', label='Light Mode'),
                ]
            )
        ]
    )


def clear_page(q: Q):
    if q.client.cards:
        for card in q.client.cards:
            del q.page[card]
    q.client.cards = set()


@on()
async def approve(q: Q):
    q.app.customer_df.loc[q.app.customer_df[ID_COLUMN] == q.client.selected_customer_id, 'Status'] = 'Approved'
    await render_customer_selector(q)


@on()
async def reject(q: Q):
    q.app.customer_df.loc[q.app.customer_df[ID_COLUMN] == q.client.selected_customer_id, 'Status'] = 'Rejected'
    await render_customer_selector(q)


@on()
async def dark_mode(q: Q):
    q.page['meta'].theme = 'neon'


@on()
async def light_mode(q: Q):
    q.page['meta'].theme = 'default'


@on('customer_table')
async def render_customer_page(q: Q):

    clear_page(q)

    row_index = int(q.args.customer_table[0])
    customer_row = q.app.customer_df.loc[row_index]
    score = q.app.predictions_df.loc[row_index]
    approve = bool(score < APPROVAL_THRESHOLD)
    contribs = q.app.contributions_df.loc[row_index].drop("BiasTerm")

    q.client.selected_customer_id = customer_row["ID"]

    # details
    q.client.cards.add('customer_features')
    q.page['customer_features'] = ui.form_card(
        box='customer_features',
        items=[
            ui.table(
                name='customer_features',
                columns=[
                    ui.table_column(name="attribute", label="Attribute", sortable=False, searchable=False, max_width='100'),
                    ui.table_column(name="value", label="Value", sortable=False, searchable=False, max_width='100')
                ],
                rows=[ui.table_row(name=index, cells=[index, row]) for index, row in customer_row.map(str).iteritems()],
                groupable=False,
                resettable=False,
                multiple=False,
                height='760px'
            )
        ]
    )

    # summary
    top_feature = contribs.idxmin(axis=1) if approve else contribs.idxmax(axis=1)
    explanation_data = {
        'will_or_will_not': 'will' if approve else 'will not',
        'top_contributing_feature': top_feature,
        'value_of_top_contributing_feature': str(customer_row[top_feature]),
        'accept_or_reject': 'approve' if approve else 'reject',
    }
    explanation = (
        "- This customer **{{will_or_will_not}}** most probably settle the next month credit card balance.\n"
        "- Having a **{{top_contributing_feature}}** of **{{value_of_top_contributing_feature}}** is the top reason for that.\n"
        "- It's a good idea to **{{accept_or_reject}}** this customer." 
    )
    q.client.cards.add('customer_risk_explanation')
    q.page["customer_risk_explanation"] = ui.markdown_card(
        box='customer_risk_explanation',
        title='Summary on Customer',
        content='=' + explanation,
        data=explanation_data,
    )

    # shap plot
    shap_values = list(zip(contribs.index, contribs))
    shap_values.sort(key=lambda x: x[1])
    q.client.cards.add('customer_shap_plot')
    q.page['customer_shap_plot'] = ui.plot_card(
        box='customer_shap_plot',
        title="Effectiveness of each attribute on defaulting next payment",
        data=data(['label', 'value'], rows=shap_values),
        plot=ui.plot([ui.mark(type='interval', x='=value', x_title='SHAP value', y='=label')])
    )

    # approve/reject buttons
    q.client.cards.add('button_group')
    q.page["button_group"] = ui.form_card(
        box='button_group',
        items=[
            ui.buttons(
                [
                    ui.button(name='approve', label='Approve', primary=approve),
                    ui.button(name='reject', label='Reject', primary=not approve),
                ]
            )
        ]
    )


async def render_customer_selector(q: Q):

    clear_page(q)

    columns = [ui.table_column(name=column, label=column, sortable=True, searchable=True) for column in q.app.customer_df.columns]
    rows = [ui.table_row(name=str(index), cells=row.tolist()) for index, row in q.app.customer_df.applymap(str).iterrows()]
    q.client.cards.add('customer_table')
    q.page["customer_table"] = ui.form_card(
        box='customer_table',
        items=[
            ui.message_bar(text='Click "Status" to review a customer', type='info'),
            ui.table(
                name='customer_table',
                columns=columns,
                rows=rows,
                groupable=True,
                multiple=False,
            )
        ]
    )


@app("/")
async def serve(q: Q):
    if not q.app.initialized:
        init_app(q)
    if not q.client.initialized:
        init_client(q)
    if not await handle_on(q):
        await render_customer_selector(q)
    await q.page.save()
