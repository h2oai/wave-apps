# Wave Retail Forecasting Application 

This application allows users to explore the Kaggle Walmart Sales data to understand seasonality of sales by department. This application uses predictions made from Driverless AI but doesn't explictily connect to a DAI instance.


## Running this App Locally

_This has only been tested on OSX._

1. Download a release of Wave and have that running

2. Create a python environment in the home app directory and install reqirements
`make setup`

3. Activate the virtual environment
`source venv/bin/activate`

4. Run the app by pointing to the module directory
`wave run src.app`

Point your web browswer to `localhost:55555`
In the future, if you want to run this app you can skip step 2 as the environment is already set up.
