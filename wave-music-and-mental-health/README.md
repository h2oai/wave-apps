# Effect of Music on Mental Health

![music and mental Health](music_and_mental_health.gif)

## Introduction

> This project aims to investigate the relationship between music and mental health. We will be looking at how different types of music can affect an individual's mood and overall psychological well-being. The dataset from [Kaggle](https://www.kaggle.com/datasets/catherinerasgaitis/mxmh-survey-results)
>
> The ultimate goal is to gain a better understanding of the ways in which music can be used as a tool to promote mental health and well-being.

### Step 5: Build a dashboard to present your finds using `h2o_wave` (available in the `src` folder)

In the final step of the project, we will use the h2o_wave library to build a dashboard to present our findings. A dashboard is a user-friendly interface that allows users to interact with and explore the data and results of our analysis. We will be using [h2o_wave](https://wave.h2o.ai/), which is a fast and simple dashboard tool for Python created by [h2o.ai](https://h2o.ai/)

## Running the project(Dashboard)

Once we have completed all of the above steps and built the dashboard, we will be ready to run the project and share our findings with others. To run the dashboard, do the following:

1. create a virtual environment with the command:

```bash
python -m venv .myenv
```

2. Activate the virtual environment

```bash
source .myenv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Navigate to the `src` folder and run:

```bash
wave run src/app.py
```

5. Point your browser to `http://localhost:10101` to view the app.
