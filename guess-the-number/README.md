# Guess The Number

A simple game to learn [User Authentication][wave-single-sign-on], and the difference between [`q.app`, `q.user`, and `q.client`][wave-app-state] in a Wave app.

This app is a single player game where the player guesses the number picked by the
computer. All players that are logged into the same app instance can compare their
scores against each other.

#### Table Of Contents

- [Running this App Locally](#running-this-app-locally)
    - [1. Install Wave Server](#1-download-the-latest-release-of-wave-and-have-that-running)
    - [2. Create a python environment](#2-create-a-python-environment-in-the-app-directory-and-install-requirements)
    - [3. Run the app](#3-run-the-app-by-pointing-to-the-module-directory)
- [Setup User Authentication](#setup-user-authentication)
- [More Screenshots](#more-screenshots)
    - [Welcome Screen](#welcome-screen)
    - [Start the game](#start-the-game)
    - [Guess the Number](#guess-the-number-1)
    - [Complete the Game](#complete-the-game)
    - [View Scores](#view-scores)
    - [View Scores from your games only](#view-scores-from-your-games-only)

![game progress][screenshot-progress]

[Top](#table-of-contents)

## Running this App Locally

#### 1. Download the latest release of Wave and have that running

- Read instructions from [Wave Documentation][wave-docs-installation]

![wave installation][wave-installation-term-gif]

[Top](#table-of-contents)

#### 2. Create a python environment in the app directory and install requirements

- Need Python `3.7.9 +`

```console
$ git clone https://github.com/h2oai/wave-apps.git
$ cd wave-apps/guess-the-number
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

![wave-app-env-setup-term-gif]

[Top](#table-of-contents)

#### 3. Run the app by pointing to the module directory

```console
$ wave run guess_the_number/guess.py
```

- Point your web browser to `localhost:10101`. In the future, if you want to run this app you can skip step 2 as the environment is already set up.

[Top](#table-of-contents)

## Setup User Authentication

The previous section will help get the app up and running. However, the player is always `Default-User`. Follow the instructions at [Run `waved` with authentication during development using keycloak][auth-dev-setup-keycloak] to have the ability to login as a different user. Please DO NOT use these instructions for a production environment.

[Top](#table-of-contents)

## More Screenshots

#### Welcome Screen

![game intro][screenshot-0]

[Top](#table-of-contents)

#### Start the game

![game start][screenshot-1]

[Top](#table-of-contents)

#### Guess the Number

![game progress][screenshot-progress]

[Top](#table-of-contents)

#### Complete the Game

![game done][screenshot-done]

[Top](#table-of-contents)

#### View Scores

![game scores][screenshot-scores]

[Top](#table-of-contents)

#### View Scores from your games only

![game private scores][screenshot-private-scores]

[Top](#table-of-contents)

[screenshot-0]: ./static/guess_the_number_0.png
[screenshot-1]: ./static/guess_the_number_1.png
[screenshot-progress]: ./static/guess_the_number_progress.png
[screenshot-done]: ./static/guess_the_number_done.png
[screenshot-scores]: ./static/guess_the_number_scores.png
[screenshot-private-scores]: ./static/guess_the_number_private_scores.png
[wave-installation-gif]: ./static/install_wave_server.gif
[wave-installation-term-gif]: ./static/install_wave_server_term.gif
[wave-app-env-setup-term-gif]: ./static/wave_app_env_setup_term.gif
[wave-docs-installation]: https://h2oai.github.io/wave/docs/installation
[wave-app-state]: https://h2oai.github.io/wave/docs/state
[wave-single-sign-on]: https://h2oai.github.io/wave/docs/security#single-sign-on
[auth-dev-setup-keycloak]: ./dev_authentication_setup.md
