from typing import List, Optional
import pandas as pd

from h2o_wave import app, main, Q, ui, data
from .churn_predictor import ChurnPredictor

TRAIN_DATASET_PATH = './data/churnTrain.csv'
TEST_DATASET_PATH = './data/churnTest.csv'
TARGET_COLUMN = "Churn?"
CATEGORICAL_COLUMNS = ['Area Code']
DROP_COLUMNS = ["Phone"]

df = pd.read_csv(TEST_DATASET_PATH)
df.dropna(inplace=True)
df['Total Charges'] = (df['Day Charges'] + df['Evening Charges'] + df['Night Charges'] + df['Intl Charges'])

churn_predictor = ChurnPredictor(
    train_dataset_path=TRAIN_DATASET_PATH,
    test_dataset_path=TEST_DATASET_PATH,
    target_column=TARGET_COLUMN,
    categorical_columns=CATEGORICAL_COLUMNS,
    drop_columns=DROP_COLUMNS,
)


def render_shap_plot(q: Q, shap_rows: List, selected_row_index: Optional[int]):
    q.page['shap_plot'] = ui.plot_card(
        box=ui.box('top-plot', height='700px'),
        title='Shap explanation' if selected_row_index else 'Global Shap',
        data=data(['label', 'value'], rows=shap_rows),
        plot=ui.plot(
            [ui.mark(type='interval', x='=value', x_title='SHAP value', y='=label', color=q.client.secondary_color)])
    )


def render_negative_pdp_plot(q: Q, shap_rows: List, selected_row_index: Optional[int]):
    min_contrib_col = shap_rows[-1][0] if selected_row_index is None else None
    is_cat, min_contrib_col, retention_rows = churn_predictor.get_negative_explanation(selected_row_index,
                                                                                       min_contrib_col)
    plot = [
        ui.mark(type='interval', x='=label', y='=size', x_title=min_contrib_col, color=q.client.secondary_color,
                fill_opacity=0.5),
        ui.mark(type='line' if is_cat else 'point', x='=label', y='=value', color=q.client.primary_color,
                shape='circle'),
    ]
    if selected_row_index is not None:
        plot.append(ui.mark(x=churn_predictor.get_python_type(df[min_contrib_col][selected_row_index])))
    q.page['top_negative_plot'] = ui.plot_card(
        box='middle',
        title='Feature Most Contributing to Retention',
        data=data(['label', 'value', 'size'], rows=retention_rows),
        plot=ui.plot(plot)
    )


def render_positive_pdp_plot(q: Q, shap_rows: List, selected_row_index: Optional[int]):
    max_contrib_col = shap_rows[0][0] if selected_row_index is None else None
    is_cat, max_contrib_col, churn_rows = churn_predictor.get_positive_explanation(selected_row_index, max_contrib_col)
    plot = [
        ui.mark(type='interval', x='=label', y='=size', x_title=max_contrib_col, color=q.client.secondary_color,
                fill_opacity=0.5),
        ui.mark(type='line' if is_cat else 'point', x='=label', y='=value', color=q.client.primary_color,
                shape='circle'),
    ]
    if selected_row_index is not None:
        plot.append(ui.mark(x=churn_predictor.get_python_type(df[max_contrib_col][selected_row_index])))
    q.page['top_positive_plot'] = ui.plot_card(
        box='middle',
        title='Feature Most Contributing to Churn',
        data=data(['label', 'value', 'size'], rows=churn_rows),
        plot=ui.plot(plot)
    )


def render_desc_info(q: Q, selected_row_index: Optional[int]):
    churn_rate = churn_predictor.get_churn_rate(selected_row_index)
    q.page['churn_rate'] = ui.tall_gauge_stat_card(
        box='top-stats',
        title='Churn Rate' if selected_row_index else 'Average Churn Prediction',
        value='={{intl churn minimum_fraction_digits=2 maximum_fraction_digits=2}}%',
        aux_value='',
        progress=churn_rate / 100,
        plot_color=q.client.secondary_color,
        data=dict(churn=churn_rate)
    )

    total_charges = df['Total Charges']
    charge = total_charges[selected_row_index] if selected_row_index is not None else total_charges.mean(axis=0)
    rank = df['Total Charges'].rank(pct=True).values[selected_row_index] if selected_row_index is not None else df[
        'Total Charges'].rank(pct=True).mean(axis=0)
    q.page['total_charges'] = ui.tall_gauge_stat_card(
        box='top-stats',
        title='Total Charges' if selected_row_index else 'Average Total Charges',
        value="=${{intl charge minimum_fraction_digits=2 maximum_fraction_digits=2}}",
        aux_value='={{intl rank style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=q.client.secondary_color,
        progress=rank,
        data=dict(charge=charge, rank=rank),
    )


def render_charges_breakdown(q: Q, selected_row_index: Optional[int]):
    labels = ['Day Charges', 'Evening Charges', 'Night Charges', 'Intl Charges']
    rows = []
    for label in labels:
        if selected_row_index is not None:
            rows.append((label, df[label][selected_row_index]))
        else:
            rows.append((label, df[label].mean(axis=0)))
    color_range = f'{q.client.primary_color} {q.client.secondary_color} {q.client.tertiary_color} #67dde6'
    q.page['bar_chart'] = ui.plot_card(
        box=ui.box('top-stats', height='300px'),
        title='Total call charges breakdown' if selected_row_index else 'Average Charges Breakdown',
        data=data(['label', 'value'], rows=rows),
        plot=ui.plot([ui.mark(type='interval', x='=label', y='=value', color='=label', color_range=color_range)])
    )


def render_analysis_page(q: Q):
    q.page['title'] = ui.section_card(
        box='title',
        title='Customer profiles from model predictions',
        subtitle='Customer: No customer chosen',
        items=[
            ui.picker(
                name='customers',
                label='Customer Phone Number',
                choices=[ui.choice(name=str(phone), label=str(phone)) for phone in df['Phone']],
                max_choices=1,
                trigger=True
            ),
            ui.toggle(name='theme', label='Dark Theme', trigger=True)
        ]
    )

    row_phone_no = int(q.args.customers[0]) if q.args.customers else None
    q.page['title'].items[0].picker.values = q.args.customers
    q.page['title'].subtitle = f'Customer: {row_phone_no or "No customer selected"}'
    selected_row_index = int(df[df['Phone'] == row_phone_no].index[0]) if row_phone_no else None

    shap_rows = churn_predictor.get_shap(selected_row_index)
    render_shap_plot(q, shap_rows, selected_row_index)
    render_negative_pdp_plot(q, shap_rows, selected_row_index)
    render_positive_pdp_plot(q, shap_rows, selected_row_index)
    render_desc_info(q, selected_row_index)
    render_charges_breakdown(q, selected_row_index)


def render_my_page(q: Q):
    q.page['my_page'] = ui.form_card(
        box=ui.box('my_page', height='calc(100vh - 155px)'),
        title='This is my page',
        items=[
            ui.text('Hello World!')
        ]
    )


def init(q: Q):
    q.client.primary_color = '$blue'
    q.client.secondary_color = '$cyan'
    q.client.tertiary_color = '$azure'
    q.page['meta'] = ui.meta_card(box='', title='Telco Churn Analytics', layouts=[
        ui.layout(breakpoint='xs', zones=[
            ui.zone('header'),
            ui.zone('title'),
            ui.zone('content', zones=[
                ui.zone('my_page'),
                ui.zone('top', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('top-plot', size='70%'),
                    ui.zone('top-stats')
                ]),
                ui.zone('middle', direction=ui.ZoneDirection.ROW),
            ])
        ])
    ])
    q.page['header'] = ui.header_card(
        box='header',
        title='Telecom Churn Analytics',
        subtitle='EDA & Churn Modeling with AutoML & Wave',
        nav=[
            ui.nav_group('Main Menu', items=[
                ui.nav_item(name='analysis', label='Analysis'),
                ui.nav_item(name='my_page', label='My Page'),
            ])
        ]
    )


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        init(q)
        q.client.initialized = True

    dark_theme = q.args.theme
    if dark_theme is not None:
        if dark_theme:
            q.page['meta'].theme = 'neon'
            q.client.primary_color = '$yellow'
            q.client.secondary_color = '$lime'
            q.client.tertiary_color = '$amber'
        else:
            q.page['meta'].theme = 'default'
            q.client.primary_color = '$blue'
            q.client.secondary_color = '$cyan'
            q.client.tertiary_color = '$azure'
        q.page['title'].items[1].toggle.value = dark_theme

    if q.args.my_page:
        del q.page['title']
        del q.page['shap_plot']
        del q.page['top_negative_plot']
        del q.page['top_positive_plot']
        del q.page['total_charges']
        del q.page['bar_chart']
        del q.page['churn_rate']
        render_my_page(q)
    else:
        del q.page['my_page']
        render_analysis_page(q)

    await q.page.save()
