from test.e2e import walkthrough

import pandas as pd
import os

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from h2o_wave import app, main, Q, ui, data
from .churn_predictor import ChurnPredictor

df = pd.read_csv('data/churnTest.csv')
df.dropna(subset=['State', 'Account_Length', 'Area_Code', 'Phone_No'], inplace=True)
df.fillna({'International_Plan': 'no', 'Voice_Mail_Plan': 'no', 'No_Vmail_Messages': 0, 'Total_Day_minutes': 0.00,
           'Total_Day_Calls': 0, 'Day Charges': 0.00, 'Total_Eve_Minutes': 0.00, 'Total_Eve_Calls': 0,
           'Evening Charges': 0, 'Total_Night_Minutes': 0.00, 'Total_Night_Calls': 0, 'Night Charges': 0.00,
           'Total_Intl_Minutes': 0.00, 'Total_Intl_Calls': 0, 'Intl Charges': 0.00, 'No_CS_Calls': 0},
          inplace=True)
df['Total Charges'] = (df['Day Charges'] + df['Evening Charges'] + df['Night Charges'] + df['Intl Charges'])
rank = df['Total Charges'].rank(pct=True).values[0]
churn_predictor = ChurnPredictor()


def render_analysis(q: Q):
    row_phone_no = int(q.args.customers[0]) if q.args.customers else None
    q.page['title'].items[0].picker.values = q.args.customers
    q.page['title'].subtitle = f'Customer: {row_phone_no or "No customer selected"}'
    selected_row_index = int(df[df['Phone_No'] == row_phone_no].index[0]) if row_phone_no else None

    shap_rows = churn_predictor.get_shap(selected_row_index)
    q.page['shap_plot'] = ui.plot_card(
        box=ui.box('top-plot', height='700px'),
        title='Shap explanation',
        data=data(['label', 'value'], rows=shap_rows),
        plot=ui.plot([ui.mark(type='interval', x='=value', x_title='SHAP value', y='=label', color=q.client.secondary_color)])
    )

    min_contrib_col = shap_rows[-1][0] if selected_row_index is None else None
    is_cat, min_contrib_col, retention_rows = churn_predictor.get_negative_explanation(selected_row_index, min_contrib_col)
    plot = [
        ui.mark(type='interval', x='=label', y='=size', x_title=min_contrib_col, color=q.client.secondary_color, fill_opacity=0.5),
        ui.mark(type='line' if is_cat else 'point', x='=label', y='=value', color=q.client.primary_color, shape='circle'),
    ]
    if selected_row_index is not None:
        plot.append(ui.mark(x=churn_predictor.get_python_type(df[min_contrib_col][selected_row_index])))
    q.page['top_negative_plot'] = ui.plot_card(
        box='middle',
        title='Feature Most Contributing to Retention',
        data=data(['label', 'value', 'size'], rows=retention_rows),
        plot=ui.plot(plot)
    )

    max_contrib_col = shap_rows[0][0] if selected_row_index is None else None
    is_cat, max_contrib_col, churn_rows = churn_predictor.get_positive_explanation(selected_row_index, max_contrib_col)
    plot = [
        ui.mark(type='interval', x='=label', y='=size', x_title=max_contrib_col, color=q.client.secondary_color, fill_opacity=0.5),
        ui.mark(type='line' if is_cat else 'point', x='=label', y='=value', color=q.client.primary_color, shape='circle'),
    ]
    if selected_row_index is not None:
        plot.append(ui.mark(x=churn_predictor.get_python_type(df[max_contrib_col][selected_row_index])))
    q.page['top_positive_plot'] = ui.plot_card(
        box='middle',
        title='Feature Most Contributing to Churn',
        data=data(['label', 'value', 'size'], rows=churn_rows),
        plot=ui.plot(plot)
    )

    churn_rate = churn_predictor.get_churn_rate(selected_row_index)
    q.page['churn_rate'] = ui.tall_gauge_stat_card(
        box='top-stats',
        title='Churn Rate',
        value='={{intl churn minimum_fraction_digits=2 maximum_fraction_digits=2}}%',
        aux_value='',
        progress=churn_rate / 100,
        plot_color=q.client.secondary_color,
        data=dict(churn=churn_rate)
    )

    total_charges = df['Total Charges']
    charge = total_charges[selected_row_index] if selected_row_index is not None else total_charges.mean(axis=0)
    q.page['total_charges'] = ui.tall_gauge_stat_card(
        box='top-stats',
        title='Total Charges',
        value="=${{intl charge minimum_fraction_digits=2 maximum_fraction_digits=2}}",
        aux_value='={{intl rank style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=q.client.secondary_color,
        progress=rank,
        data=dict(charge=charge, rank=rank),
    )

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
        title='Total call charges breakdown',
        data=data(['label', 'value'], rows=rows),
        plot=ui.plot([ui.mark(type='interval', x='=label', y='=value', color='=label', color_range=color_range)])
    )


def render_code(q: Q):
    local_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(local_dir, 'app.py')) as f:
        contents = f.read()

    py_lexer = get_lexer_by_name("python")
    html_formatter = HtmlFormatter(full=True, style="xcode")
    q.page['code'] = ui.frame_card(box=ui.box('code', height='calc(100vh - 155px)'), title='', content=highlight(contents, py_lexer, html_formatter))

def init(q: Q):
    q.page['meta'] = ui.meta_card(box='', title='Telco Churn Analytics', layouts=[
        ui.layout(breakpoint='xs', zones=[
            ui.zone('header'),
            ui.zone('title'),
            ui.zone('content', zones=[
                ui.zone('empty'),
                ui.zone('code'),
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
                ui.nav_item(name='#analysis', label='Analysis'),
                ui.nav_item(name='#code', label='Application Code'),
            ])
        ]
    )
    q.page['title'] = ui.section_card(
        box='title',
        title='Customer profiles from model predictions',
        subtitle='Customer: No customer chosen',
        items=[
            # TODO: Replace with dropdown after https://github.com/h2oai/wave/pull/303 merged.
            ui.picker(
                name='customers',
                label='Customer Phone Number',
                choices=[ui.choice(name=str(phone), label=str(phone)) for phone in df['Phone_No']],
                max_choices=1,
                trigger=True
            ),
            ui.toggle(name='theme', label='Dark Theme', trigger=True)
        ]
    )


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        init(q)
        q.client.primary_color = '$blue'
        q.client.secondary_color = '$cyan'
        q.client.tertiary_color = '$azure'
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

    if q.args['#'] == 'code':
        del q.page['empty']
        del q.page['shap_plot']
        del q.page['top_negative_plot']
        del q.page['top_positive_plot']
        del q.page['total_charges']
        del q.page['bar_chart']
        del q.page['churn_rate']
        render_code(q)
    else:
        del q.page['code']
        render_analysis(q)

    await q.page.save()
