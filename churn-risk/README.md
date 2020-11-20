# Wave Telecom Customer Churn Application

This application allows users to explore the [Kaggle Churn Data](https://www.kaggle.com/c/churn-analytics-bda/data) to understand more about when and why customers are churning. 

## Developer Guide 

### Prerequisite 
1. Python 3.8+
2. pip3
3. JRE 11+

#### Run on local machine 

_This has only been tested only on OSX._

1. Download a [Wave](https://github.com/h2oai/wave/releases) version higher than 0.9.0 and have that running. 
2. Create a python environment in the home app directory and install requirements. 
    ```bash
    make setup
    ```
3. Activate the virtual environment 

```bash 
source venv/bin/activate
```

. Run the app by pointing to the module directory
```bash
wave run src.app
```

4. Point your web browswer to localhost:55555

5. Generate test coverage report.

```bash
pytest --cov={APP_SOURCE_DIRECTORY} --cov-report html
```
This will generate an html report inside htmlcov directory.

In the future, if you want to run this app you can skip step 2 as the environment is already set up
