# Shopping Cart Recommendations app

Provide product suggestions based on user's active cart using market basket analysis. 

### Screenshots from App

![Shopping Cart Recommendations App Screenshot](docs/screenshots/shopping-app.png)

## Developer Guide 

### Prerequisite 
1. Python 3.7+
2. pip3

### Run app on local machine 

1. Download the latest [Wave](https://github.com/h2oai/wave/releases) version and have that running. 
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
