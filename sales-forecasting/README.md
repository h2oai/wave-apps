# Wave Retail Forecasting Application 

This application allows users to explore the Kaggle Walmart Sales data to understand seasonality of sales by department.
This application uses predictions made from Driverless AI but doesn't explicitly connect to a DAI instance.

![Screenshot of the app][screenshot-main]

## Running this App Locally

### 1. Download the latest release of Wave and have that running

- Read instructions from [Wave Documentation][wave-docs-installation]

### 2. Create a python environment in the home app directory and install requirements

- Need Python `3.7.9`

```console
$ git clone git@github.com:h2oai/wave-apps.git
$ cd wave-apps/sales-forecasting
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### 3. Download input data from AWS S3

```console
$ cd wave-apps/sales-forecasting
$ s3cmd get s3://ai.h2o.benchmark/temp/walmart_train.csv .
$ s3cmd get s3://ai.h2o.benchmark/temp/walmart_test_preds.csv .
```

### 4. Run the app by pointing to the module directory

```console
$ wave run wave-forecast
```

- Point your web browser to `localhost:10101`. In the future, if you want to run this app you can skip steps 2 and 3 as
  the environment is already set up.

[screenshot-main]: ./static/wave_sales_forecast.png "Screenshot of the app"
[wave-docs-installation]: https://h2oai.github.io/wave/docs/installation
