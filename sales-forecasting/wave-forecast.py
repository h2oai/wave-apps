import os
import sys
from h2o_wave import main, ui, Q, app

import altair as alt
import boto3
import botocore
import pandas as pd


# Disable max row limit of 5000 for Altair
_ = alt.data_transformers.disable_max_rows()


# Define a custom font for Altair. This is the font used by Wave.
def my_font():
    font_name = "Inter"
    return {
        "config": {
            "title": {"font": font_name},
            "axis": {"labelFont": font_name, "titleFont": font_name},
            "header": {"labelFont": font_name, "titleFont": font_name},
            "legend": {"labelFont": font_name, "titleFont": font_name},
        }
    }


# Enable Altair to use Inter as font
_ = alt.themes.register("my_font", my_font)
_ = alt.themes.enable("my_font")

walmart_train_s3 = "s3://ai.h2o.benchmark/temp/walmart_train.csv"
walmart_predictions_s3 = "s3://ai.h2o.benchmark/temp/walmart_test_preds.csv"
walmart_train = './walmart_train.csv'
walmart_predictions = './walmart_test_preds.csv'


def download_file_from_s3(s3_uri, file_path):
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not all([access_key, secret_key]):
        return None
    if not s3_uri.startswith('s3://'):
        return None

    bucket_name, *key = s3_uri.split('s3://')[-1].split('/')
    file_key = '/'.join(key)
    file_local_path = os.path.abspath(file_path)

    try:
        s3 = boto3.resource(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )
        s3.Bucket(bucket_name).download_file(file_key, file_local_path)
    except botocore.exceptions.ClientError as error:
        print("Unable to connect to S3!")
        print(error)
        return None
    else:
        return file_local_path


def plot_data(stores, departments, n_test_set):

    stores = [int(i) for i in stores]
    departments = [int(i) for i in departments]

    df_train = pd.read_csv(walmart_train)
    df_train['data_type'] = 'History'

    df_preds = pd.read_csv(walmart_predictions)
    df_preds['data_type'] = 'Predictions'
    df_preds = df_preds[df_preds['Date'].isin(list(df_preds['Date'].unique()[0:n_test_set]))]

    df = df_train.append(df_preds)

    subset = df[df['Store'].isin(stores) & df['Dept'].isin(departments)].reset_index(drop=True)

    # Colors from Wave default Theme.
    # https://github.com/h2oai/wave/blob/4ec0f6a6a2b8f43f11cdb557ba35a540ad23c13c/ui/src/theme.ts#L86
    blue = '#2196F3'
    orange = '#FF9800'

    chart = (
        alt.Chart(subset)
        .mark_circle(size=40)
        .encode(
            x=alt.X(
                'Date:T',
                axis=alt.Axis(
                    title='Date',
                    labelFontSize=12,
                    titleFontSize=14,
                    titlePadding=20,
                ),
            ),
            y=alt.Y(
                'Weekly_Sales:Q',
                axis=alt.Axis(
                    title='Weekly Sales',
                    labelFontSize=12,
                    titleFontSize=14,
                    titlePadding=20,
                ),
            ),
            color=alt.Color(
                'data_type:N',
                scale=alt.Scale(domain=['History', 'Predictions'], range=[blue, orange]),
                sort=alt.EncodingSortField('data_type', order='ascending'),
                legend=alt.Legend(labelFontSize=12, title="Data Type"),
            ),
            tooltip=[
                alt.Tooltip('Date:T', format='%A, %B %d %Y'),
                'Store',
                'Dept',
                alt.Tooltip('Weekly_Sales:Q', format=',.0~f')
            ]
        )
        .properties(height=500, width=1200)
    ).configure_view(
        fillOpacity=0,
    ).interactive()

    spec = chart.to_json()
    return spec


def get_selection_content(stores, departments, forecast_horizon):

    train_df = pd.read_csv(walmart_train)
    test_df = pd.read_csv(walmart_predictions)

    stores_unique = train_df['Store'].unique()
    stores_choices = [ui.choice(name=str(i), label=str(i)) for i in stores_unique]

    departments_unique = train_df['Dept'].unique()
    departments_choices = [ui.choice(name=str(i), label=str(i)) for i in departments_unique]

    forcast_choices = [ui.choice(name=str(i), label=str(i)) for i in range(len(test_df['Date'].unique()))]

    items = [
        ui.separator('Select Area of Interest'),
        ui.dropdown(name='store_selection', label='Store IDs', values=stores, required=True, choices=stores_choices),
        ui.dropdown(name='department_selection', label='Product IDs', values=departments, required=True,
                    choices=departments_choices),
        ui.button(name='selection_button', label='Submit', primary=True),

        ui.frame(content=' ', height="40px"),

        ui.separator('Generate Sales Forecast'),
        ui.dropdown(name='forecast_horizon', label='Number of Weeks', value=str(forecast_horizon), required=True,
                    choices=forcast_choices),
        ui.button(name='forcast_button', label='Submit', primary=True),
    ]
    return items


async def initialize_app(q: Q):

    # Download input data from S3
    train = download_file_from_s3(walmart_train_s3, walmart_train)
    if train is None or not os.path.isfile(train):
        sys.exit(1)
    pred = download_file_from_s3(walmart_predictions_s3, walmart_predictions)
    if pred is None or not os.path.isfile(pred):
        sys.exit(1)

    # simple default values
    q.app.store_selection = ['1', '2', '3', '4', '5', '6']
    q.app.department_selection = ['3']
    q.app.forecast_horizon = 0

    # Setup UI elements on the page
    q.page['meta'] = ui.meta_card(box='', title='H2O Wave')
    q.page['title'] = ui.header_card(
        box='1 1 -1 1',
        title='Sales Forecasting',
        subtitle='Exploring historic demand and forecasts for supply chain optimization',
        icon='GiftBox',
        icon_color='#ffe600',
    )
    q.page['sidebar'] = ui.form_card(
        box='1 2 2 -1',
        items=get_selection_content(q.app.store_selection, q.app.department_selection, q.app.forecast_horizon)
    )
    q.page['content'] = ui.vega_card(
        box='3 2 -1 -1',
        title='Historic Weekly Sales',
        specification=plot_data(q.app.store_selection, q.app.department_selection, q.app.forecast_horizon),
    )


@app('/walmart')
async def serve(q: Q):

    print(q.args)

    if not q.client.app_initialized:
        await initialize_app(q)
        q.client.app_initialized = True

    if q.args.selection_button:
        q.page['sidebar'].items = [ui.progress('Processing data request...')]
        await q.page.save()

        q.app.store_selection = q.args.store_selection or q.app.store_selection
        q.app.department_selection = q.args.department_selection or q.app.department_selection

        q.page['sidebar'].items = get_selection_content(q.app.store_selection, q.app.department_selection,
                                                        q.app.forecast_horizon)
        q.page['content'].specification = plot_data(q.app.store_selection, q.app.department_selection,
                                                    q.app.forecast_horizon)

    if q.args.forcast_button:
        q.page['sidebar'].items = [ui.progress('Forecasting demand...')]
        await q.page.save()

        q.app.forecast_horizon = int(q.args.forecast_horizon)

        q.page['sidebar'].items = get_selection_content(q.app.store_selection, q.app.department_selection,
                                                        q.app.forecast_horizon)
        q.page['content'].specification = plot_data(q.app.store_selection, q.app.department_selection,
                                                    q.app.forecast_horizon)

    await q.page.save()
