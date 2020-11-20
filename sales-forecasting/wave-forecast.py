import os
import sys
from dataclasses import asdict, dataclass, field
from typing import List, Optional

import boto3
import botocore
import pandas as pd
from h2o_wave import app, data, main, Q, ui


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
        if q_args.departments:
            self.departments = [int(x) for x in q_args.departments]
        if q_args.n_forecast_weeks:
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
        ui.text_l('**Select Area of Interest**'),
        ui.dropdown(
            name='stores',
            label='Store IDs',
            values=[str(x) for x in user_inputs.stores],
            choices=[ui.choice(name=str(x), label=str(x)) for x in sales_data.stores_unique],
            tooltip='Select the Stores to include in the prediction',
            trigger=True,
        ),
        ui.text_xs('⠀'),
        ui.dropdown(
            name='departments',
            label='Product IDs',
            values=[str(x) for x in user_inputs.departments],
            choices=[ui.choice(name=str(x), label=str(x)) for x in sales_data.departments_unique],
            tooltip='Select the Products to include in the prediction',
            trigger=True,
        ),
        ui.frame(content=' ', height="40px"),
        ui.text_l('**Generate Sales Forecast**'),
        ui.slider(
            name='n_forecast_weeks',
            label='Number of Weeks',
            min=0,
            max=len(sales_data.prediction_dates) - 1,
            step=1,
            value=user_inputs.n_forecast_weeks,
            trigger=True,
            tooltip='Select the number of weeks into the future to predict'
        ),
        ui.text_xs('⠀'),
        ui.button(
            name='reset',
            label='Reset',
            primary=True,
            tooltip='Click to reset all values to defaults'
        ),
        ui.text_xs('⠀'),
        ui.progress(label='', caption='', visible=progress),
    ]


async def draw_weekly_sales_plot(q: Q, plot_data):
    # del q.page['content']
    # Colors from Wave default Theme.
    # https://github.com/h2oai/wave/blob/4ec0f6a6a2b8f43f11cdb557ba35a540ad23c13c/ui/src/theme.ts#L86
    blue_orange = '#2196F3 #FF9800'
    v = q.page.add(
        'content',
        ui.plot_card(
            box='4 2 9 9',
            title='Walmart Weekly Sales Forecast',
            data=data('Date Weekly_Sales data_type', len(plot_data)),
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
                    color_range=blue_orange,
                    shape='circle'
                )
            ])
        ))
    v.data = plot_data
    await q.page.save()


async def initialize_app(q: Q):
    # Inputs for the app, Should be read from a config file
    walmart_train_s3 = "s3://ai.h2o.benchmark/temp/walmart_train.csv"
    walmart_predictions_s3 = "s3://ai.h2o.benchmark/temp/walmart_test_preds.csv"
    walmart_train = './walmart_train.csv'
    walmart_predictions = './walmart_test_preds.csv'

    # Setup UI elements on the page
    q.page['meta'] = ui.meta_card(box='', title='H2O Wave - Sales Forecasting')
    q.page['title'] = ui.header_card(
        box='1 1 12 1',
        title='Sales Forecasting',
        subtitle='Exploring historic demand and forecasts for supply chain optimization',
        icon='GiftBox',
        icon_color='#ffe600',
    )
    q.page['loading'] = ui.form_card(
        box='4 4 6 1',
        items=[ui.progress(label='Downloading sales data from AWS S3 ...', caption='')]
    )
    await q.page.save()

    # Download input data from S3
    train = download_file_from_s3(walmart_train_s3, walmart_train, overwrite=False)
    if train is None or not os.path.isfile(train):
        sys.exit(1)
    pred = download_file_from_s3(walmart_predictions_s3, walmart_predictions, overwrite=False)
    if pred is None or not os.path.isfile(pred):
        sys.exit(1)

    q.page['loading'].items[0].progress.label = 'Processing sales data ...'
    await q.page.save()

    # Create default UserInputs and SalesData
    q.app.user_inputs = UserInputs()
    q.app.user_inputs.reset()
    q.app.sales_data = SalesData(walmart_train, walmart_predictions)

    plot_data = q.app.sales_data.get_plot_data(**asdict(q.app.user_inputs))

    del q.page['loading']
    q.page['sidebar'] = ui.form_card(
        box='1 2 3 9',
        items=get_user_input_items(q.app.sales_data, q.app.user_inputs)
    )
    await draw_weekly_sales_plot(q, plot_data)


@app('/walmart')
async def serve(q: Q):
    print(q.args)

    if not q.client.app_initialized:
        await initialize_app(q)
        q.client.app_initialized = True
        return

    q.app.user_inputs.update(q.args)

    q.page['sidebar'].items = get_user_input_items(q.app.sales_data, q.app.user_inputs, progress=True)
    await q.page.save()

    plot_data = q.app.sales_data.get_plot_data(**asdict(q.app.user_inputs))
    q.page['sidebar'].items[10].progress.visible = False
    await draw_weekly_sales_plot(q, plot_data)
