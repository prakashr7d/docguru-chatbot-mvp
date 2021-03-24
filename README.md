# Dash E-Comm Bot

This is a bot for our e-comm demo.
A bot that will take care of all of your shopping needs in one go.

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

# Dev Setup

### `PYTHONPATH` setup

- Pycharm: Mark `./src` as content root
- Others: Set this environment variable `export PYTHONPATH=./src`

### Environment Setup
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


# How to run the bot with docker

### Train a model if needed

### Build the Docker image

Then, to setup image run:
```commandline
docker-compose build
```

### Train a model

```shell script
docker-compose run rasa-x poetry run rasa train
```

### Start all the services

Then, start `docker-compose.yml` to start all servers:
```commandline
docker-compose up
```

`config.yml`, `credentials.yml` and `enpoints.yml` get added to the docker image. 
Make sure to rebuild the image after making changes to these files.

### Checkout the demo
Once all the containers are up go to [http://localhost:7000](http://localhost:7000)


# How to run the bot without docker

### Train a model
```shell script
poetry run rasa train --config config-local.yml
```

### Start action server
Then, to run, first set up your action server in one terminal window:
```bash
poetry run rasa run actions
```

### Start Duckling server
In another window, run the duckling server (for entity extraction):
```bash
docker run -p 8000:8000 rasa/duckling
```

### Start Rasa server
Then talk to your bot by running:
```
poetry run rasa run --enable-api --cors "*" --endpoints endpoints-local.yml
```

### [OPTIONAL] Run Rasa shell in Debug mode
poetry run rasa shell --debug --endpoints endpoints-local.yml

Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working
under the hood. To simply talk to the bot, you can remove this flag.


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
5. Adding `stories` directly into 'stories' or into their respective files
6. Add `intents` directly into `nlu.yml' or into their respective files
7. Add `rules` directly into `rules.yml` or into their respective files
6. Why to do this? <hr>
    1. Rasa x makes formating different and its not clean at all
    2. This will make flow bad and when added too many use cases it will look mess <hr>
7. Add `actions` as needed while doing interactive training
8. Make sure to follow clean code methodology
9. Commit code every day even if you did very less addition
