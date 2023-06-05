# Getting Started with H2O Wave

This project was bootstrapped with `wave init` command.

## Running the app

Make sure you have activated a Python virtual environment with `h2o-wave` installed.

If you haven't created a python env yet, simply run the following command (assuming Python 3.7 is installed properly).

For MacOS / Linux:

```sh
python3 -m venv venv
source venv/bin/activate
pip install h2o-wave
```

For Windows:

```sh
python3 -m venv venv
venv\Scripts\activate.bat
pip install h2o-wave
```

Once the virtual environment is setup and active, run:

```sh
# To run first example
wave run app1.py

# To run thelast example App
wave run app13.py
```

Which will start a Wave app at <http://localhost:10101>.



## Application topics

This is is the set of applications (from app1 to app13) which demonstrate how to develop Wave application step by step. Each step adds additional functionality.

List of training Apps:

- `app1` through `app8` - step by step development of Employee Churn dashboard
- `app9` - adding debugging and logging
- `app10 `- refactoring app9 to refresh content only when there is a change due to user interaction. In the previous steps we have re-drawn cards every time there was a change
- `app11` - This app is the same as `app10`, but it pulls data from Delta Lake storage.
- `app12` - This app adds pagination logic to `app10`.
- `app13` - This app adds tabs and tab switching to `app12`. Cards are recreated only when tab switching is detected.



## Interactive Wave University examples

If you don't feel like going through the docs because you are more of a hands-on person, you can try our Wave University app.

Within your activated virtual environment, run:

```sh
wave learn
```



The command requires `h2o_wave_university` to be installed. To do that, run:

```sh
pip install h2o_wave_university
```



Wave University documentation link: https://wave.h2o.ai/docs/getting-started#interactive-learning 



## Learn More

To learn more about H2O Wave, check out the [docs](https://wave.h2o.ai/).
