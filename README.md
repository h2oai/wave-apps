# Wave Telecom Customer Churn Application

This application allows users to explore the [Kaggle Churn Data](https://www.kaggle.com/c/churn-analytics-bda/data) to understand more about when and why customers are churning. 

#### Running this App Locally
_This has only been tested on OSX._

1. Download a release of Wave and have that running

2. Create a python environment in the home app directory and install reqirements 
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

In the future, if you want to run this app you can skip step 2 as the environment is already set up
