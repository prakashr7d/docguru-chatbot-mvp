# Dash E-Comm Bot

#### This is a bot for our e-comm demo
#### A bot that will take care of all of your shopping needs in one go.

## Features:
- [x] Login n Logout
- [x] Order status
- [ ] Product Return/Replace
- [ ] Product Inquiry
- [ ] Personalize shopping and so on....

# Prerequisites
- Python 3.7
    If you don't have Python3.7, then consider [installing conda with python3.7](https://phoenixnap.com/kb/how-to-install-anaconda-ubuntu-18-04-or-20-04). 
    Once you have installed it, activate the base environment and then run the following instructions.
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/)

# How to run the bot with docker

To get started, check `Dockerfile` for packages and modules

Then, to setup image run:
```commandline
sudo docker build -t "dash-ecomm:latest"
```
Then, start `docker-compose.yml` to start all servers:
```commandline
sudo docker-compose up -d
```

Every url in `config.yml`, `credentials.yml` and `enpoints.yml` are connected to docker images.

# How to run the bot without docker

Use `rasa train` to train a model.

Then, to run, first set up your action server in one terminal window:
```bash
poetry run rasa run actions
```

In another window, run the duckling server (for entity extraction):
```bash
docker run -p 8000:8000 rasa/duckling
```

Then talk to your bot by running:
```
poetry run rasa shell --debug
```

Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working
under the hood. To simply talk to the bot, you can remove this flag.

# `PYTHONPATH` setup

- Pycharm: Mark `./src` as content root
- Others: Set this environment variable `export PYTHONPATH=./src`

# Dev Setup
Use the following command 

- **A Makefile** with various helpful targets. E.g.,
  ```bash
  # to install system level dependencies
  make bootstrap
   
  # Configuring NS Private PyPi repo
  # Get username and password from the project Admin
  poetry config http-basic.neuralspace <private-pypi-username> <private-pypi-password>

  # install virtual environment and project level dependencies
  make install
  
  # run unit tests
  make test
  
  # run black code formatting and isort
  make format
  
  # to run flake8 and validate code formatting
  make lint
  ```


## Overview of the files

`data/stories` - contains stories

`data/nlu` - contains NLU training data

`data/rules.yml` - contains rules

`actions.py` - contains custom action/api code

`domain.yml` - the domain file, including bot response templates

`config.yml` - training configurations for the NLU pipeline and policy ensemble

`tests/test_stories.yml` - end-to-end test stories


## Testing the bot

You can test the bot on test conversations by running  `rasa test`.
This will run [end-to-end testing](https://rasa.com/docs/rasa/user-guide/testing-your-assistant/#end-to-end-testing) on the conversations in `tests/test_stories.yml`.

Note that if duckling isn't running when you do this, you'll see some failures.

## Development workflow
##### Development workflow with just 9 simple steps

1. Start development with initializing rasa bot
2. While, developing bot first start with creating intents.
3. Now, start `Rasa X` and start interactive training
4. Add `utters` as needed directly to `domain.yml` instead of using `Rasa X` for adding them
5. Add `stories` directly into 'stories' or into their respective files
6. Add `intents` directly into `nlu.yml` or into their respective files
7. Add `rules` directly into `rules.yml` or into their respective files
6. Why to do this? <hr>
    1. Rasa x makes formating different and its not clean at all
    2. This will make flow bad and when added too many use cases it will look mess <hr>
7. Add `actions` as needed while doing interactive training
8. Make sure to follow clean code methodology
9. Commit code every day even if you did very less addition
