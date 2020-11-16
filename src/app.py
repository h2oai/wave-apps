from h2o_wave import Q, ui, app, main

import pandas as pd
import numpy as np
from .utils import ui_table_from_df, python_code_content
from .plots import html_hist_of_target_percent, html_map_of_target_percent, stat_card_dollars
from .config import Configuration

config = Configuration()


def home_content(training_file_url, header_png):
    df = pd.read_csv(config.working_data).head()

    items = [
        ui.text_xl('User Guide'),
        ui.frame(content=' ', height="20px"),  # whitespace

        ui.text(f'![{config.y_col}]({header_png})'),
        ui.frame(content=' ', height="20px"),  # whitespace

        ui.text('''This Churn Prediction application allows for exploring historical churn data, building a predictive 
        churn model, and exploring those predictions. Dashboards are available to understand both global trends and 
        the behavior of each customer.'''),
        ui.frame(content=' ', height="20px"),  # whitespace

        ui.separator("Data"),
        ui.frame(content=' ', height="20px"),  # whitespace

        ui.text(f'The historic training data comes packaged with this application. You can find out more about it from '
                f'[this Kaggle page](https://www.kaggle.com/c/churn-analytics-bda/overview). Click '
                f'[here]({training_file_url}) to download the training dataset.'),
        ui.frame(content=' ', height="20px"),  # whitespace

        ui_table_from_df(df, 5, "Training Data")

    ]

    return items


# TODO currently 3 cols hard coded, make this more general
def dashboard_content():

    column_name = config.get_column_type()

    items = [
        ui.text_xl(f'Summary of Churn on {config.get_analysis_type()}'),
        ui.frame(content=html_map_of_target_percent(config.working_data, column_name, "State", config.color), height='60%'),
        ui.frame(content=html_hist_of_target_percent(config.working_data, column_name, "Total_Intl_Charge", config.color),
                 height='60%'),
        ui.frame(content=html_hist_of_target_percent(config.working_data, column_name, "Account_Length", config.color),
                 height='60%'),

    ]

    return items


def profile_content():
    df = pd.read_csv(config.working_data).head(40)

    choices = [ui.choice(name=phone, label=f'{phone}') for phone in df[config.id_column]]

    items = [
        ui.text_xl(f'Customer Profiles from {config.get_analysis_type()}'),
        ui.picker(name='customers', label=f'Customer Phone Number', choices=choices, max_choices=1),
        ui.button(name='select_customer_button', label='Submit', primary=True)
    ]
    return items


async def profile_selected_page(q: Q):
    df = pd.read_csv(config.working_data)

    # q.page["content"].items = [ui.text_xl(content="Values and Percentiles for Customer: " + str(q.args.customers[0]))]
    # print(df[q.args.customers['Churn?']])
    if config.model_loaded:
        churn_pct = df[df[config.id_column] == q.args.customers]['Churn.1'].values[0]

        if churn_pct > 0.5:
            color = '$red'
        else:
            color = '$green'

        q.page['churn_stat'] = ui.tall_gauge_stat_card(
            box='4 4 1 2',
            title="Likelihood to Churn",
            value='={{intl foo style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='',
            plot_color=color,
            progress=churn_pct,
            data=dict(foo=churn_pct, bar=0),
        )

    df['Total Charges'] = df.Total_Day_charge + df.Total_Eve_Charge + df.Total_Night_Charge + df.Total_Intl_Charge
    df = df[["Total_Day_charge", "Total_Eve_Charge", "Total_Night_Charge", "Total_Intl_Charge", config.id_column,
             "Total Charges"]]
    df.columns = ["Day Charges", "Evening Charges", "Night Charges", "Int'l Charges", config.id_column, "Total Charges"]
    q.page["day_stat"]  = stat_card_dollars(df, q.args.customers[0], "Day Charges", '5 2 1 2', config.color)
    q.page["eve_stat"] = stat_card_dollars(df, q.args.customers[0], "Evening Charges", '6 2 1 2', config.color)
    q.page["night_stat"] = stat_card_dollars(df, q.args.customers[0], "Night Charges", '7 2 1 2', config.color)
    q.page["intl_stat"] = stat_card_dollars(df, q.args.customers[0], "Int'l Charges", '5 4 1 2', config.color)
    q.page["total_stat"] = stat_card_dollars(df, q.args.customers[0], "Total Charges", '7 4 1 2', config.total_gauge_color)
    q.page['customer'] = ui.markdown_card(box='3 2 2 1', title='Customer', content=str(q.args.customers[0]))
    q.page['prediction'] = ui.markdown_card(box='8 2 -1 4', title='Churn Rate', content=str(q.args.customers[0]))


async def initialize_page(q: Q):

    content = []

    if not q.client.app_initialized:
        q.app.header_png, = await q.site.upload([config.image_path])
        q.app.training_file_url, = await q.site.upload([config.working_data])
        content = home_content(q.app.training_file_url, q.app.header_png)
        q.client.app_initialized = True

    q.page.drop()

    q.page['title'] = ui.header_card(
        box='1 1 -1 1',
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page['side_bar'] = ui.nav_card(
        box='1 2 2 -1',
        items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#home', label='Home'),
                ui.nav_item(name='#dashboard', label='Global Dashboard'),
                ui.nav_item(name='#profile', label='Customer Profiles'),
                ui.nav_item(name='#tour', label='Application Code'),
            ])
        ],
    )
    q.page['content'] = ui.form_card(
        box='3 2 -1 -1',
        items=content
    )

    await q.page.save()


@app('/')
async def serve(q: Q):

    await initialize_page(q)
    content = q.page["content"]

    if q.args.select_customer_button:
        await profile_selected_page(q)

    elif q.args.select_model_button:
        content.items = [ui.progress(label="Making Predictions in Driverless AI")]
        await q.page.save()

        predictions_file_url, = await q.site.upload([config.working_data])

        df = pd.read_csv(config.working_data)

        content.items = [
            ui.text_xl(f"{config.y_col} Predictions have been Made on New Data"),
            ui.frame(content=' ', height="20px"),  # whitespace
            ui.text(
                f"See the Dashboard and Customer Profiles for the results! "
                f"[Download the model predictions]({predictions_file_url})."),
            # ui_table_from_df(df, 10, 'predictions')
        ]

    else:
        hash = q.args['#']

        if hash == 'home':
            content.items = home_content(q.app.training_file_url, q.app.header_png)

        elif hash == 'dashboard':
            content.items = dashboard_content()

        elif hash == 'profile':
            content.items = profile_content()

        elif hash == 'tour':
            content.items = python_code_content('app.py')

    await q.page.save()
