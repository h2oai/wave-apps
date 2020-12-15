# Wave Telecom Customer Churn Application

This application allows users to explore the [Kaggle Churn Data](https://www.kaggle.com/c/churn-analytics-bda/data) 
to understand more about when and why customers are churning. 

### Screenshots from App

![Chrun App Screenshot - 1](docs/screenshots/churn-app-1.png)
![Chrun App Screenshot - 2](docs/screenshots/churn-app-2.png)
![Chrun App Screenshot - 3](docs/screenshots/churn-app-3.png)

## Developer Guide 

### Prerequisite 
1. Python 3.8+
2. pip3
3. JRE 11+

### Run app on local machine 

_This has only been tested only on OSX._

1. Download a [Wave](https://github.com/h2oai/wave/releases) version higher than 0.9.0 and have that running. 
2. Create a python virtual environment in the home app directory and install requirements. 
    ```bash
    make setup
    ```
3. Activate the virtual environment.
    ```bash 
    source venv/bin/activate
    ```
4. Run the app with Wave CLI.
    ```bash
    wave run src.app
    ```
5. Point your web browser to [localhost:10101](http://localhost:10101)

After the initial setup, you can skip step 2 and 3 as the virtual environment is already available.

