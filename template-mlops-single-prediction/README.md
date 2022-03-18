# Template: Single Predictions from H2O MLOps Deployments

This application will dynamically create a web-form to interact with an 
MLOps deployment. Send feature to get predictions back immediately for regression, 
binary, and multi-classification problems.

Parameterize this app for your own use cases and deployments by updating the `app.toml` file. You 
can find the source code at https://github.com/h2oai/wave-apps/template-mlops-single-prediction

## Local Development Setup

1. Setup your local python environment
```shell script
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

2. Run the template
We use the `H2O_WAVE_NO_LOG` parameter to only show logs from our app, 
not from the app server.

```shell script
H2O_WAVE_NO_LOG=True ./venv/bin/wave run app.py
```

## HAIC Deployment
To publish this app to the H2O AI Cloud, use the [h2o CLI](https://h2oai-cloud-release.s3.amazonaws.com/releases/ai/h2o/h2o-cloud/latest/index.html).
```shell script
h2o bundle import -v ALL_USERS
```

Make sure to update the app.toml with your use case values.