# Guess The Number

## Screenshots

![game completed](static/game_done.png)

![scores](static/scores.png)

## Running this App Locally

### 1. Download the latest release of Wave and have that running

- Read instructions from [Wave Documentation][wave-docs-installation]

### 2. Create a python environment in the home app directory and install requirements

- Need Python Python 3.7+

```console
$ git clone git@github.com:h2oai/wave-apps.git
$ cd wave-apps/guess-the-number
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### 3. Run the app by pointing to the module directory

```console
$  wave run guess_the_number.guess
```

- Point your web browser to `localhost:10101`. In the future, if you want to run this app you can skip steps 2 and 3 as
  the environment is already set up.

