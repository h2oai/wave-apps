from typing import List, Optional
import pandas as pd
import os

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from h2o_wave import app, main, Q, ui, data
from .churn_predictor import ChurnPredictor


TRAIN_DATASET_PATH='./data/insurance_churn_train.csv'
TEST_DATASET_PATH='./data/insurance_churn_test.csv'
TARGET_COLUMN="churn"
CATEGORICAL_COLUMNS=[
    'churn', 
    'RISK_RATED_AREA_B', 
    'RISK_RATED_AREA_C', 
    'ROOF_CONSTRUCTION', 
    'WALL_CONSTRUCTION', 
    'LISTED',
    'OWNERSHIP_TYPE',
    'PAYING_GUESTS',
    'PROP_TYPE',
]
DROP_COLUMNS=['Police', 'i', 'POL_STATUS', 'CAMPAIGN_DESC']
VARIABLE_DESCRIPTIONS = {
    "QUOTE_DATE": "Day quote was made",
    "COVER_START": "Beginning of the cover payment",
    "CLAIM3YEARS": "Loss in last 3 years",
    "P1_EMP_STATUS": "Client's professional status",
    "P1_PT_EMP_STATUS": "Client's part-time professional status",
    "BUS_USE": "Commercial use indicator",
    "CLERICAL": "Administration office usage indicator",
    "AD_BUILDINGS": "Building coverage - Self damage",
    "RISK_RATED_AREA_B": "Geographical Classification of Risk - Building",
    "SUM_INSURED_BUILDINGS": "Sum Assured - Building",
    "NCD_GRANTED_YEARS_B": "Bonus Malus - Building",
    "AD_CONTENTS": "Coverage of personal items - Self damage",
    "RISK_RATED_AREA_C": "Geographical Classification of Risk - Personal Objects",
    "SUM_INSURED_CONTENTS": "Sum Assured - Personal Items",
    "NCD_GRANTED_YEARS_C": "Malus Bonus - Personal Items",
    "CONTENTS_COVER": "Coverage - Personal Objects indicator",
    "BUILDINGS_COVER": "Cover - Building indicator",
    "SPEC_SUM_INSURED": "Sum Assured - Valuable Personal Property",
    "SPEC_ITEM_PREM": "Premium - Personal valuable items",
    "UNSPEC_HRP_PREM": "Premium - Unspecified",
    "P1_DOB": "Date of birth of the client",
    "P1_MAR_STATUS": "Marital status of the client",
    "P1_POLICY_REFUSED": "Policy Emission Denial Indicator",
    "P1_SEX": "Client's sex",
    "APPR_ALARM": "Appropriate alarm",
    "APPR_LOCKS": "Appropriate lock",
    "BEDROOMS": "Number of bedrooms",
    "ROOF_CONSTRUCTION": "Code of the type of construction of the roof",
    "WALL_CONSTRUCTION": "Code of the type of wall construction",
    "FLOODING": "House susceptible to floods",
    "LISTED": "National Heritage Building",
    "MAX_DAYS_UNOCC": "Number of days unoccupied",
    "NEIGH_WATCH": "Neighborhood watch present",
    "OCC_STATUS": "Occupancy status",
    "OWNERSHIP_TYPE": "Type of membership",
    "PAYING_GUESTS": "Presence of paying guests",
    "PROP_TYPE": "Type of property",
    "SAFE_INSTALLED": "Safe installs",
    "SEC_DISC_REQ": "Reduction of premium for security",
    "SUBSIDENCE": "Subsidence indicator",
    "YEARBUILT": "Year of construction",
    "CAMPAIGN_DESC": "Description of the marketing campaign",
    "PAYMENT_METHOD": "Method of payment",
    "PAYMENT_FREQUENCY": "Frequency of payment",
    "LEGAL_ADDON_PRE_REN": "Option 'Legal Fees' included before 1st renewal",
    "LEGAL_ADDON_POST_REN": "Option 'Legal Fees' included after 1st renewal",
    "HOME_EM_ADDON_PRE_REN": "Option 'Emergencies' included before 1st renewal",
    "HOME_EM_ADDON_POST_REN": "Option 'Emergencies' included after 1st renewal",
    "GARDEN_ADDON_PRE_REN": "Option 'Gardens' included before 1st renewal",
    "GARDEN_ADDON_POST_REN": "Option 'Gardens' included after 1st renewal",
    "KEYCARE_ADDON_PRE_REN": "Option 'Replacement of keys' included before 1st renewal",
    "KEYCARE_ADDON_POST_REN": "Option 'Replacement of keys' included after 1st renewal",
    "HP1_ADDON_PRE_REN": "Option 'HP1' included before 1st renewal",
    "HP1_ADDON_POST_REN": "Option 'HP1' included after 1st renewal",
    "HP2_ADDON_PRE_REN": "Option 'HP2' included before 1st renewal",
    "HP2_ADDON_POST_REN": "Option 'HP2' included after renewal",
    "HP3_ADDON_PRE_REN": "Option 'HP3' included before 1st renewal",
    "HP3_ADDON_POST_REN": "Option 'HP3' included after renewal",
    "MTA_FLAG": "Mid-Term Adjustment indicator",
    "MTA_FAP": "Bonus up to date of Adjustment",
    "MTA_APRP": "Adjustment of the premium for Mid-Term Adjustment",
    "MTA_DATE": "Date of Mid-Term Adjustment",
    "LAST_ANN_PREM_GROSS": "Premium - Total for the previous year",
    "POL_STATUS": "Policy status",
    "Police": "Policy number",
}

df = pd.read_csv(TEST_DATASET_PATH)
df.fillna(0, inplace=True) # to avoid 'Out of range float values are not JSON compliant'
df['Total Sum Assured'] = (df['SUM_INSURED_BUILDINGS'] + df['SUM_INSURED_CONTENTS'] + df['SPEC_SUM_INSURED'])
rank = df['Total Sum Assured'].rank(pct=True).values[0]

churn_predictor = ChurnPredictor(
    train_dataset_path=TRAIN_DATASET_PATH,
    test_dataset_path=TEST_DATASET_PATH,
    target_column=TARGET_COLUMN,
    categorical_columns=CATEGORICAL_COLUMNS,
    drop_columns=DROP_COLUMNS,
)


def render_shap_plot(q: Q, shap_rows: List, selected_row_index: Optional[int]):
    shap_rows = [(VARIABLE_DESCRIPTIONS[x[0]], x[1]) for x in shap_rows]
    q.page['shap_plot'] = ui.plot_card(
        box=ui.box('top-plot', height='900px'),
        title='Shap explanation' if selected_row_index else 'Global Shap',
        data=data(['label', 'value'], rows=shap_rows),
        plot=ui.plot([ui.mark(type='interval', x='=value', x_title='SHAP value', y='=label', color=q.client.secondary_color)])
    )


def render_negative_pdp_plot(q: Q, shap_rows: List, selected_row_index: Optional[int]):
    min_contrib_col = shap_rows[-1][0] if selected_row_index is None else None
    is_cat, min_contrib_col, retention_rows = churn_predictor.get_negative_explanation(selected_row_index, min_contrib_col)
    plot = [
        ui.mark(type='interval', x='=label', y='=size', x_title=VARIABLE_DESCRIPTIONS[min_contrib_col], color=q.client.secondary_color, fill_opacity=0.5),
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


def render_positive_pdp_plot(q: Q, shap_rows: List, selected_row_index: Optional[int]):
    max_contrib_col = shap_rows[0][0] if selected_row_index is None else None
    is_cat, max_contrib_col, churn_rows = churn_predictor.get_positive_explanation(selected_row_index, max_contrib_col)
    plot = [
        ui.mark(type='interval', x='=label', y='=size', x_title=VARIABLE_DESCRIPTIONS[max_contrib_col], color=q.client.secondary_color, fill_opacity=0.5),
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


def render_desc_info(q: Q, selected_row_index: Optional[int]):
    churn_rate = churn_predictor.get_churn_rate(selected_row_index)
    q.page['churn_rate'] = ui.tall_gauge_stat_card(
        box='top-stats',
        title='Churn Rating' if selected_row_index else 'Average Churn Prediction',
        value='={{intl churn minimum_fraction_digits=2 maximum_fraction_digits=2}}%',
        aux_value='',
        progress=churn_rate / 100,
        plot_color=q.client.secondary_color,
        data=dict(churn=churn_rate)
    )

    total_sum_assured = df['Total Sum Assured']
    charge = total_sum_assured[selected_row_index] if selected_row_index is not None else total_sum_assured.mean(axis=0)
    q.page['total_sum_assured'] = ui.tall_gauge_stat_card(
        box='top-stats',
        title='Total Sum Assured' if selected_row_index else 'Average Total Sum Assured',
        value="=${{intl charge minimum_fraction_digits=2 maximum_fraction_digits=2}}",
        aux_value='={{intl rank style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=q.client.secondary_color,
        progress=rank,
        data=dict(charge=charge, rank=rank),
    )


def render_charges_breakdown(q: Q, selected_row_index: Optional[int]):
    labels = ['SUM_INSURED_BUILDINGS', 'SUM_INSURED_CONTENTS', 'SPEC_SUM_INSURED']
    rows = []
    for label in labels:
        if selected_row_index is not None:
            rows.append((VARIABLE_DESCRIPTIONS[label][len("Assured sum -"):], df[label][selected_row_index]))
        else:
            rows.append((VARIABLE_DESCRIPTIONS[label][len("Assured sum -"):], df[label].mean(axis=0)))
    color_range = f'{q.client.primary_color} {q.client.secondary_color} {q.client.tertiary_color} #67dde6'
    q.page['bar_chart'] = ui.plot_card(
        box=ui.box('top-stats', height='300px'),
        title='Total Sum Assured Breakdown' if selected_row_index else 'Average Total Sum Assured Breakdown',
        data=data(['label', 'value'], rows=rows),
        plot=ui.plot([ui.mark(type='interval', x='=label', y='=value', color='=label', color_range=color_range)])
    )


def render_analysis(q: Q):
    row_policy_no = q.args.customers[0] if q.args.customers else None
    q.page['title'].items[0].picker.values = q.args.customers
    q.page['title'].subtitle = f'Customer: {row_policy_no or "No customer selected"}'
    selected_row_index = int(df[df['Police'] == row_policy_no].index[0]) if row_policy_no else None
    shap_rows = churn_predictor.get_shap(selected_row_index)
    render_shap_plot(q, shap_rows, selected_row_index)
    render_negative_pdp_plot(q, shap_rows, selected_row_index)
    render_positive_pdp_plot(q, shap_rows, selected_row_index)
    render_desc_info(q, selected_row_index)
    render_charges_breakdown(q, selected_row_index)


def render_code(q: Q):
    local_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(local_dir, 'app.py')) as f:
        contents = f.read()

    py_lexer = get_lexer_by_name("python")
    html_formatter = HtmlFormatter(full=True, style="xcode")
    q.page['code'] = ui.frame_card(box=ui.box('code', height='calc(100vh - 155px)'), title='', content=highlight(contents, py_lexer, html_formatter))


def init(q: Q):
    q.client.primary_color = '$blue'
    q.client.secondary_color = '$cyan'
    q.client.tertiary_color = '$azure'
    q.page['meta'] = ui.meta_card(box='', title='Home Insurance Churn Analytics', layouts=[
        ui.layout(breakpoint='xs', zones=[
            ui.zone('header'),
            ui.zone('title'),
            ui.zone('content', zones=[
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
        title='Home Insurance Churn Analytics',
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
                label='Customer Policy Number',
                choices=[ui.choice(name=str(policy), label=str(policy)) for policy in df['Police']],
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
        del q.page['shap_plot']
        del q.page['top_negative_plot']
        del q.page['top_positive_plot']
        del q.page['total_sum_assured']
        del q.page['bar_chart']
        del q.page['churn_rate']
        render_code(q)
    else:
        del q.page['code']
        render_analysis(q)

    await q.page.save()
