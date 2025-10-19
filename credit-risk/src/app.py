import pandas as pd
from h2o_wave import app, data, handle_on, main, on, Q, ui

from .model import Model


TRAIN_CSV = './data/Kaggle/CreditCard-train.csv'
TEST_CSV = './data/Kaggle/CreditCard-train.csv'  # In practice, use a separate test set
ID_COLUMN = 'ID'
TARGET_COLUMN = 'default.payment.next.month'
APPROVAL_THRESHOLD = 0.35


def init_app(q: Q):
    q.app.initialized = True
    q.app.model = Model(TRAIN_CSV, ID_COLUMN, TARGET_COLUMN)
    
    # Load FULL test dataset (not just 20 rows)
    df = pd.read_csv(TEST_CSV)
    df = df.copy()
    df.drop(TARGET_COLUMN, axis=1, inplace=True)
    
    # Generate predictions & contributions
    q.app.predictions_df = q.app.model.predict(df)
    q.app.contributions_df = q.app.model.contrib(df)
    
    # Prepare display DataFrame
    df['Default Prediction Rate'] = q.app.predictions_df.round(4)
    df.insert(loc=0, column='Status', value='Pending', allow_duplicates=True)
    q.app.customer_df = df


def init_client(q: Q):
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = ui.meta_card(
        box='', 
        title='Credit Risk', 
        layouts=[
            ui.layout(
                breakpoint='xs',
                zones=[
                    ui.zone('header'),
                    ui.zone('customer_table'),
                    ui.zone('customer_page', size='800px'),
                ]
            ),
            ui.layout(
                breakpoint='m',
                zones=[
                    ui.zone('header'),
                    ui.zone('customer_table'),
                    ui.zone('customer_page', size='800px'),
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
            ui.nav_group('Navigation', items=[ui.nav_item(name='render_customer_selector', label='Customers')]),
            ui.nav_group('Options', items=[
                ui.nav_item(name='dark_mode', label='Dark Mode'),
                ui.nav_item(name='light_mode', label='Light Mode'),
            ])
        ]
    )


def clear_page(q: Q):
    for card in list(q.client.cards):
        if card in q.page:
            del q.page[card]
    q.client.cards = set()


@on()
async def approve(q: Q):
    if q.client.selected_customer_id is not None:
        q.app.customer_df.loc[q.app.customer_df[ID_COLUMN] == q.client.selected_customer_id, 'Status'] = 'Approved'
    await render_customer_selector(q)


@on()
async def reject(q: Q):
    if q.client.selected_customer_id is not None:
        q.app.customer_df.loc[q.app.customer_df[ID_COLUMN] == q.client.selected_customer_id, 'Status'] = 'Rejected'
    await render_customer_selector(q)


@on()
async def dark_mode(q: Q):
    q.page['meta'].theme = 'h2o-dark'
    await render_customer_selector(q)


@on()
async def light_mode(q: Q):
    q.page['meta'].theme = 'default'
    await render_customer_selector(q)


@on('customer_table')
async def render_customer_page(q: Q):
    clear_page(q)

    # Get selected row index
    if not q.args.customer_table:
        return
    row_index = int(q.args.customer_table[0])
    customer_row = q.app.customer_df.iloc[row_index]
    score = q.app.predictions_df.iloc[row_index]
    approve_flag = bool(score < APPROVAL_THRESHOLD)
    contribs = q.app.contributions_df.iloc[row_index].drop('BiasTerm')

    q.client.selected_customer_id = customer_row[ID_COLUMN]

    # Customer features table
    q.client.cards.add('customer_features')
    q.page['customer_features'] = ui.form_card(
        box='customer_page',
        items=[
            ui.table(
                name='customer_features',
                columns=[
                    ui.table_column(name='attribute', label='Attribute', max_width='150'),
                    ui.table_column(name='value', label='Value', max_width='150')
                ],
                rows=[ui.table_row(name=str(i), cells=[str(k), str(v)]) for i, (k, v) in enumerate(customer_row.items())],
                height='400px'
            )
        ]
    )

    # Risk explanation
    top_feature = contribs.idxmin() if approve_flag else contribs.idxmax()
    explanation_data = {
        'will_or_will_not': 'will' if approve_flag else 'will not',
        'top_contributing_feature': top_feature,
        'value_of_top_contributing_feature': str(customer_row[top_feature]),
        'accept_or_reject': 'approve' if approve_flag else 'reject',
    }
    explanation = (
        "- This customer **{{will_or_will_not}}** most probably settle the next month credit card balance.\n"
        "- Having a **{{top_contributing_feature}}** of **{{value_of_top_contributing_feature}}** is the top reason for that.\n"
        "- It's recommended to **{{accept_or_reject}}** this customer."
    )
    q.client.cards.add('customer_risk_explanation')
    q.page['customer_risk_explanation'] = ui.markdown_card(
        box='customer_page',
        title='Summary on Customer',
        content='=' + explanation,
        data=explanation_data,
    )

    # SHAP plot
    shap_values = [(col, float(val)) for col, val in contribs.items()]
    shap_values.sort(key=lambda x: x[1])
    q.client.cards.add('customer_shap_plot')
    q.page['customer_shap_plot'] = ui.plot_card(
        box='customer_page',
        title='Effectiveness of each attribute on defaulting next payment',
        data=data(['label', 'value'], rows=shap_values),
        plot=ui.plot([ui.mark(type='interval', x='=value', x_title='Feature Contributions', y='=label')])
    )

    # Action buttons
    q.client.cards.add('button_group')
    q.page['button_group'] = ui.form_card(
        box='customer_page',
        items=[
            ui.buttons([
                ui.button(name='approve', label='Approve', primary=approve_flag),
                ui.button(name='reject', label='Reject', primary=not approve_flag),
            ])
        ]
    )


async def render_customer_selector(q: Q):
    clear_page(q)

    # Make all columns searchable and sortable
    columns = []
    for col in q.app.customer_df.columns:
        # Format numeric columns nicely
        if col == 'Default Prediction Rate':
            columns.append(ui.table_column(
                name=col,
                label=col,
                sortable=True,
                searchable=True,
                data_type=ui.TableDataType.NUMBER,
                precision=4
            ))
        else:
            columns.append(ui.table_column(
                name=col,
                label=col,
                sortable=True,
                searchable=True
            ))

    rows = []
    for idx, row in q.app.customer_df.iterrows():
        cells = [str(v) for v in row]
        rows.append(ui.table_row(name=str(idx), cells=cells))

    q.client.cards.add('customer_table')
    q.page['customer_table'] = ui.form_card(
        box='customer_table',
        items=[
            ui.message_bar(text='Click any row to review a customer', type='info'),
            ui.table(
                name='customer_table',
                columns=columns,
                rows=rows,
                multiple=False,
                height='500px',
                downloadable=True  # Optional: allow CSV export
            )
        ]
    )


@app('/')
async def serve(q: Q):
    if not q.app.initialized:
        init_app(q)
    if not q.client.initialized:
        init_client(q)
    if not await handle_on(q):
        await render_customer_selector(q)
    await q.page.save()