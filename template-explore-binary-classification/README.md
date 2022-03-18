# Template: Exploring Distributions for Binary Classification

This application will dynamically create an interactive, data-exploring app for binary 
classification use cases. The user can choose any column to get plots with distributions 
for each target class option. 

Parameterize this app for your own use cases and deployments by updating the `app.toml` file. You
can find the source code at https://github.com/h2oai/wave-apps/tree/main/template-explore-binary-classification

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
