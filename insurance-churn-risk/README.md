# Wave Home Insurance Customer Churn Application

This application builds a model using H2O Wave ML to predict which [Home Insurance Customers](https://www.kaggle.com/ycanario/home-insurance) are most likely to churn and why. Shapley values and partial dependence plots allow the user to understand why the model thinks each customer will or will not churn.

![Chrun App Screenshot](docs/screenshots/churn-risk-preview.png)

## Running this App Locally

### System Requirements

1. Python 3.6+
2. pip3
3. JRE 11+ (needed to run H2O-3)
4. NodeJS (Only needed for [Run integration tests on local machine](#run-integration-tests))

### 1. Run the Wave Server

New to H2O Wave? We recommend starting in the documentation to [download and run](https://h2oai.github.io/wave/docs/installation) the Wave Server on your local machine. Once the server is up and running you can easily use any Wave app.

### 2. Setup Your Python Environment

```bash
git clone git@github.com:h2oai/wave-apps.git
cd wave-apps/churn-risk
make setup
source venv/bin/activate
```

### 3. Run the App

```bash
wave run src.app
```

Note! If you did not activate your virtual environment this will be:

```bash
./venv/bin/wave run src.app
```

### 4. View the App

Point your favorite web browser to [localhost:10101](http://localhost:10101)

## Run Unit Tests

Optionally, you can run unit tests on this app

```bash
pytest # Run unit tests
```

```bash
pytest --cov=src --cov-report html # Run unit tests with coverage
```

This will generate a html report in `htmlcov` directory.

## Run Integration Tests

Optionally, you can run integration tests on this app

1. Go to your Wave folder downloaded in step 1 of [Run app on local machine](#running-this-app-locally).
2. Go to `test` folder inside Wave folder.
3. Run `npm install`
4. Go back to `churn-risk` app directory.
5. Here I assume I have Wave downloaded in my home directory.
If you have an already running wave instance,

```bash
python3 ~/wave/test/cypress.py -m src.app
```

else if you want to launch a new Wave instance automatically,

```bash
    python3 ~/wave/test/cypress.py -m src.app -w ~/wave/waved -wd ~/wave/www
```
