# Credit Card Risk Wave App

This application allows credit card issuers to review and approve credit card applications more analytically.

### Screenshots from App

#### Home page

![Credit Risk App Screenshot - Home Page](docs/screenshots/Credit%20Risk%20-%20Home%20Page.png)

#### Customer Page 

![Credit Risk App Screenshot - Customer Page](docs/screenshots/Credit%20Risk%20-%20Customer%20Page.png)

## Developer Guide 

### Prerequisite 
1. Python 3.7+
2. pip3
3. JRE 11+

### Run app on local machine 

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
5. Point your web browser to [localhost:55555](http://localhost:55555)

After the initial setup, you can skip step 2 and 3 as the virtual environment is already available.
