# Wave Retail Forecasting Application 

This application allows users to explore the Kaggle Walmart Sales data to understand seasonality of sales by department.
This application uses predictions made from Driverless AI but doesn't explicitly connect to a DAI instance.

## Running this App Locally

### System Requirements 
1. Python 3.7.9+
2. pip3

### 1. Run the Wave Server
New to H2O Wave? We recommend starting in the documentation to [download and run](https://h2oai.github.io/wave/docs/installation) the Wave Server on your local machine. Once the server is up and running you can easily use any Wave app. 

### 2. Setup Your Python Environment

```bash
$ git clone https://github.com/h2oai/wave-apps.git
$ cd wave-apps/sales-forecasting
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### 3. Download input data from AWS S3

```console
$ cd wave-apps/sales-forecasting
$ wget https://h2o-benchmark.s3.amazonaws.com/walmart-sales-forecasting/walmart_train.csv
$ wget https://h2o-benchmark.s3.amazonaws.com/walmart-sales-forecasting/walmart_test_preds.csv
```

### 4. Run the App

```bash
wave run wave_forecast
```

Note! If you did not activate your virtual environment this will be:
```bash
./venv/bin/wave run wave_forecast.py
```

### 5. View the App
Point your favorite web browser to [localhost:10101](http://localhost:10101)
