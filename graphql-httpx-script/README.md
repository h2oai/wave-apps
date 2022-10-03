# GraphQL and HTTPX Script

This script allows users to build a simple dashboard that shows how H2O Wave compares against its main competitors in terms of popularity and codebase metrics. The main competitors in question are:

- Streamlit.
- Plotly Dash.
- R Shiny.

> check the official documentation on [apps](https://wave.h2o.ai/docs/apps) vs [scripts](https://wave.h2o.ai/docs/scripts).

## Running this Script Locally

### System Requirements
1. Python 3.7.9+
2. pip3


### 1. Setup Your Python Environment

```bash
git clone https://github.com/h2oai/wave-apps.git
cd wave-apps/graphql-httpx-script
make setup
```

### 2. Authentication tokens
For this project, we will need 2 things, necessary to communicate with API endpoints:

- Github personal access token ([see obtaining instructions](https://docs.github.com/en/graphql/guides/forming-calls-with-graphql#authenticating-with-graphql)).
- Twitter bearer token ([see obtaining instructions](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens)).

When done, to keep things simple, let’s just set them as variables.
> IMPORTANT: Do not commit them to your repo. If you wish so, rewrite them to environment variables instead.

```py
# TODO: Fill with yours.
GH_TOKEN = ''
TWITTER_BEARER_TOKEN = ''
```

### 3. Run the App

Make sure that the [Wave Server is running](https://wave.h2o.ai/docs/installation-8-20#setup) and then run the following command in your terminal:

```bash
make run
```

### 4. View the App
Point your favorite web browser to [localhost:10101](http://localhost:10101)
