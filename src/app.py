from h2o_wave import Q, ui, app, main

import pandas as pd
import numpy as np
from .utils import ui_table_from_df, python_code_content
from .plots import html_hist_of_target_percent, html_map_of_target_percent, html_pie_of_target_percent, wide_stat_card_dollars, tall_stat_card_dollars, get_image_from_matplotlib
from .config import Configuration
from .churn_predictor import ChurnPredictor

config = Configuration()
churn_predictor = ChurnPredictor()


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
    df = pd.read_csv(config.testing_data_url).head(40)

    choices = [ui.choice(name=phone, label=f'{phone}') for phone in df[config.id_column]]

    items = [
        ui.text_xl(f'Customer Profiles from {config.get_analysis_type()}'),
        ui.picker(name='customers', label=f'Customer Phone Number', choices=choices, max_choices=1),
        ui.button(name='select_customer_button', label='Submit', primary=True)
    ]
    return items


async def profile_selected_page(q: Q):
    del q.page["content"]
    df = pd.read_csv(config.testing_data_url)

    # q.page["content"].items = [ui.text_xl(content="Values and Percentiles for Customer: " + str(q.args.customers[0]))]
    # print(df[q.args.customers['Churn?']])
    cust_phone_no = q.args.customers[0]
    q.client.selected_customer_index = int(df[df[config.id_column] == cust_phone_no].index[0])

    if config.model_loaded:
        churn_pct = df[df[config.id_column] == cust_phone_no]['Churn.1'].values[0]

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
    q.page["day_stat"]  = wide_stat_card_dollars(df, cust_phone_no, "Day Charges", '3 2 2 1', config.color)
    q.page["eve_stat"] = wide_stat_card_dollars(df, cust_phone_no, "Evening Charges", '5 2 2 1', config.color)
    q.page["night_stat"] = wide_stat_card_dollars(df, cust_phone_no, "Night Charges", '3 3 2 1', config.color)
    q.page["intl_stat"] = wide_stat_card_dollars(df, cust_phone_no, "Int'l Charges", '5 3 2 1', config.color)
    q.page["total_stat"] = tall_stat_card_dollars(df, cust_phone_no, "Total Charges", '7 2 1 2', config.total_gauge_color)

    q.page['customer'] = ui.small_stat_card(box='1 2 2 1', title='Customer', value=str(cust_phone_no))
    q.page['prediction'] = ui.small_stat_card(box='1 3 2 1', title='Churn Rate',
                                              value=str(churn_predictor.get_churn_rate_of_customer(q.client.selected_customer_index)) + ' %')

    labels = ["Day Charges", "Evening Charges", "Night Charges", "Int'l Charges"]
    values = [df[df[config.id_column] == cust_phone_no][labels[0]].values[0],
              df[df[config.id_column] == cust_phone_no][labels[1]].values[0],
              df[df[config.id_column] == cust_phone_no][labels[2]].values[0],
              df[df[config.id_column] == cust_phone_no][labels[3]].values[0]]

    q.page['stat_pie'] = ui.frame_card(box='8 2 -1 2', title='Total call charges breakdown',
        content=html_pie_of_target_percent('', labels,values))

    shap_plot = churn_predictor.get_shap_explanation(q.client.selected_customer_index)
    q.page['shap_plot'] = ui.image_card(
        box='1 4 -1 11',
        title='',
        type='png',
        image=get_image_from_matplotlib(shap_plot),
    )

    top_negative_pd_plot = churn_predictor.get_top_negative_pd_explanation(q.client.selected_customer_index)
    q.page['top_negative_pd_plot'] = ui.image_card(
        box='1 15 -1 11',
        title='',
        type='png',
        image=get_image_from_matplotlib(top_negative_pd_plot),
    )

    top_positive_pd_plot = churn_predictor.get_top_positive_pd_explanation(q.client.selected_customer_index)
    q.page['top_positive_pd_plot'] = ui.image_card(
        box='1 26 -1 11',
        title='',
        type='png',
        image=get_image_from_matplotlib(top_positive_pd_plot),
    )


async def initialize_page(q: Q):

    content = []

    if not q.client.app_initialized:
        churn_predictor.build_model(config.training_data_url)
        churn_predictor.set_testing_data_frame(config.testing_data_url)
        churn_predictor.predict()

        q.app.header_png, = await q.site.upload([config.image_path])
        q.app.training_file_url, = await q.site.upload([config.working_data])
        content = home_content(q.app.training_file_url, q.app.header_png)
        q.client.app_initialized = True

    q.page.drop()

    q.page['title'] = ui.header_card(
        box='1 1 3 1',
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page['side_bar'] = ui.tab_card(
        box='4 1 -1 1',
        items=[
            ui.tab(name='#home', label='Home'),
            ui.tab(name='#dashboard', label='Global Dashboard'),
            ui.tab(name='#profile', label='Customer Profiles'),
            ui.tab(name='#tour', label='Application Code'),
        ],
    )
    q.page['content'] = ui.form_card(
        box='1 2 -1 -1',
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
