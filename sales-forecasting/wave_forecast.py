import os
import sys
from dataclasses import asdict, dataclass, field
from typing import List, Optional

import boto3
import botocore
import pandas as pd
from h2o_wave import app, data, main, Q, ui


# Inputs for the app, Should be read from a config file
walmart_train_s3 = "s3://h2o-benchmark/walmart-sales-forecasting/walmart_train.csv"
walmart_predictions_s3 = "s3://h2o-benchmark/walmart-sales-forecasting/walmart_test_preds.csv"
walmart_train = './walmart_train.csv'
walmart_predictions = './walmart_test_preds.csv'

@dataclass
class UserInputs:
    stores: Optional[List[int]] = field(default_factory=list)
    departments: Optional[List[int]] = field(default_factory=list)
    n_forecast_weeks: Optional[int] = 0

    # Default values for user inputs. Should be read from a config file
    def reset(self):
        self.stores = list(range(1, 7))
        self.departments = [3]
        self.n_forecast_weeks = 0

    def update(self, q_args):
        if q_args.reset:
            self.reset()
            return
        if q_args.stores:
            self.stores = [int(x) for x in q_args.stores]
            # Hack: Forcing limits to handle app freeze
            if len(self.stores) > 20:
                self.stores = self.stores[:20]
        if q_args.departments:
            self.departments = [int(x) for x in q_args.departments]
            # Hack: Forcing limits to handle app freeze
            if len(self.departments) > 20:
                self.departments = self.departments[:20]
        if q_args.n_forecast_weeks is not None:
            self.n_forecast_weeks = q_args.n_forecast_weeks


class SalesData:
    def __init__(self, train_dataset, predictions):
        self.train_dataset = train_dataset
        self.predictions = predictions
        self._prepare_data()

    def _prepare_data(self):
        self.df_train = pd.read_csv(self.train_dataset)
        self.df_predictions = pd.read_csv(self.predictions)
        self.df_train['data_type'] = 'History'
        self.df_predictions['data_type'] = 'Predictions'
        self.prediction_dates = list(self.df_predictions['Date'].unique())
        self.stores_unique = list(self.df_train['Store'].unique())
        self.departments_unique = list(self.df_train['Dept'].unique())

    def get_plot_data(self, stores, departments, n_forecast_weeks):
        dfp = self.df_predictions.loc[self.df_predictions['Date'].isin(self.prediction_dates[:n_forecast_weeks]), :]
        df = pd.concat([self.df_train, dfp], ignore_index=True)
        subset = df[df['Store'].isin(stores) & df['Dept'].isin(departments)].reset_index(drop=True)
        s1 = subset.drop(
            columns=['Store', 'Dept', 'Temperature', 'Fuel_Price', 'MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4',
                     'MarkDown5', 'CPI', 'Unemployment', 'IsHoliday', 'sample_weight', 'sample_weight',
                     'Weekly_Sales.lower', 'Weekly_Sales.upper'])
        return s1.values.tolist()


def download_file_from_s3(s3_uri, file_path, overwrite=True):
    file_local_path = os.path.abspath(file_path)
    if os.path.isfile(file_local_path) and not overwrite:
        return file_local_path

    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not all([access_key, secret_key]):
        return None
    if not s3_uri.startswith('s3://'):
        return None

    bucket_name, *key = s3_uri.split('s3://')[-1].split('/')
    file_key = '/'.join(key)

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


def get_user_input_items(sales_data, user_inputs, progress=False):
    return [
        ui.text_l('**Prediction Configuration**'),
        ui.dropdown(
            name='stores',
            label='Store IDs',
            values=[str(x) for x in user_inputs.stores],
            choices=[ui.choice(name=str(x), label=str(x)) for x in sales_data.stores_unique],
            trigger=True,
        ),
        ui.dropdown(
            name='departments',
            label='Product IDs',
            values=[str(x) for x in user_inputs.departments],
            choices=[ui.choice(name=str(x), label=str(x)) for x in sales_data.departments_unique],
            trigger=True,
        ),
        ui.slider(
            name='n_forecast_weeks',
            label='Weeks to predict',
            min=0,
            max=len(sales_data.prediction_dates) - 1,
            step=1,
            value=user_inputs.n_forecast_weeks,
            trigger=True,
        ),
        ui.button(name='reset', label='Reset', primary=True, tooltip='Click to reset all values to defaults'),
        ui.progress(label='', caption='', visible=progress),
    ]


async def update_sidebar(q: Q, user_inputs, progress=False):
    q.page['sidebar'].items[1].dropdown.values = [str(x) for x in user_inputs.stores]
    q.page['sidebar'].items[2].dropdown.values = [str(x) for x in user_inputs.departments]
    q.page['sidebar'].items[3].slider.value = user_inputs.n_forecast_weeks
    q.page['sidebar'].items[5].progress.visible = progress
    await q.page.save()


async def draw_weekly_sales_plot(q: Q, plot_data):
    v = q.page.add('content', ui.plot_card(
            box='content',
            title='Walmart Weekly Sales Forecast',
            data=data('Date Weekly_Sales data_type', 0),
            plot=ui.plot([
                ui.mark(
                    type='point',
                    x='=Date',
                    y='=Weekly_Sales',
                    x_scale='time',
                    y_min=0,
                    x_title='Date',
                    y_title='Weekly Sales (USD)',
                    color='=data_type',
                    color_range='$red $purple',
                    size=6,
                    fill_opacity=0.75,
                    shape='circle'
                )
            ])
        ))
    v.data = plot_data
    await q.page.save()


async def initialize_app(q: Q):
    # Setup UI elements on the page
    q.page['meta'] = ui.meta_card(box='', title='H2O Wave - Sales Forecasting', layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone('header'),
                # vh means viewport height, 70px accounts for header and spacing between cards.
                ui.zone('body', size='calc(100vh - 70px)', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('sidebar', size='350px'),
                    ui.zone('content'),
                ]),
            ]
        ),
    ])
    q.page['title'] = ui.header_card(
        box='header',
        title='Sales Forecasting',
        subtitle='Exploring historic demand and forecasts for supply chain optimization',
        icon='GiftBox',
        icon_color='#ffe600',
    )

    # Create default UserInputs and SalesData
    q.app.user_inputs = UserInputs()
    q.app.user_inputs.reset()
    q.app.sales_data = SalesData(walmart_train, walmart_predictions)

    plot_data = q.app.sales_data.get_plot_data(**asdict(q.app.user_inputs))

    q.page['sidebar'] = ui.form_card(
        box='sidebar',
        items=get_user_input_items(q.app.sales_data, q.app.user_inputs)
    )
    await draw_weekly_sales_plot(q, plot_data)

def on_startup():
    # Download input data from S3
    train = download_file_from_s3(walmart_train_s3, walmart_train, overwrite=False)
    if train is None or not os.path.isfile(train):
        sys.exit(1)
    pred = download_file_from_s3(walmart_predictions_s3, walmart_predictions, overwrite=False)
    if pred is None or not os.path.isfile(pred):
        sys.exit(1)


@app('/', on_startup=on_startup)
async def serve(q: Q):
    if not q.client.app_initialized:
        await initialize_app(q)
        q.client.app_initialized = True
        return

    q.app.user_inputs.update(q.args)
    await update_sidebar(q, q.app.user_inputs, progress=True)
    plot_data = q.app.sales_data.get_plot_data(**asdict(q.app.user_inputs))
    q.page['sidebar'].items[5].progress.visible = False
    q.page['content'].data = plot_data
    await q.page.save()
