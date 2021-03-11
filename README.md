# Dash E-Comm Bot

This is a bot for our e-comm demo


# Prerequisites
- Python 3.7
    If you don't have Python3.7, then consider [installing conda with python3.7](https://phoenixnap.com/kb/how-to-install-anaconda-ubuntu-18-04-or-20-04). 
    Once you have installed it, activate the base environment and then run the following instructions.
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/)

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

# `PYTHONPATH` setup

- Pycharm: Mark `./src` as content root
- Others: Set this environment variable `export PYTHONPATH=./src`


## Run the bot

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


## Overview of the files

`data/core.md` - contains stories

`data/nlu.md` - contains NLU training data

`actions.py` - contains custom action/api code

`domain.yml` - the domain file, including bot response templates

`config.yml` - training configurations for the NLU pipeline and policy ensemble

`tests/test_stories.yml` - end-to-end test stories


## Things you can ask the bot

1. Check the status of an order
2. Return an item
3. Cancel an item
4. Search a product inventory for shoes
5. Subscribe to product updates

The bot can handle switching forms and cancelling a form, but not resuming a form after switching yet.

The main flows have the bot retrieving or changing information in a SQLite database (the file `example.db`). You can use `initialize.db` to change the data that exists in this file.

For the purposes of illustration, the bot has orders for the following email addresses:

- `example@rasa.com`
- `me@rasa.com`
- `me@gmail.com`

And these are the shoes that should show as in stock (size, color):

```
inventory = [(7, 'blue'),
             (8, 'blue'),
             (9, 'blue'),
             (10, 'blue'),
             (11, 'blue'),
             (12, 'blue'),
             (7, 'black'),
             (8, 'black'),
             (9, 'black'),
             (10, 'black')
            ]
```

## Testing the bot

You can test the bot on test conversations by running  `rasa test`.
This will run [end-to-end testing](https://rasa.com/docs/rasa/user-guide/testing-your-assistant/#end-to-end-testing) on the conversations in `tests/test_stories.yml`.

Note that if duckling isn't running when you do this, you'll see some failures.

## Rasa X Deployment

To [deploy this bot](https://rasa.com/docs/rasa/user-guide/how-to-deploy/), it is highly recommended to make use of the
[one line deploy script](https://rasa.com/docs/rasa-x/installation-and-setup/one-line-deploy-script/) for Rasa X. As part of the deployment, you'll need to set up [git integration](https://rasa.com/docs/rasa-x/installation-and-setup/integrated-version-control/#connect-your-rasa-x-server-to-a-git-repository) to pull in your data and
configurations, and build or pull an action server image.


## Action Server Image

You will need to have docker installed in order to build the action server image. If you haven't made any changes to the action code, you can also use
the [public image on Dockerhub](https://hub.docker.com/repository/docker/cdesmar/retail-demo) instead of building it yourself.

It is recommended to use an [automated CI/CD process](https://rasa.com/docs/rasa/user-guide/setting-up-ci-cd) to keep your action server up to date in a production environment.



```


textclouddev.azurecr.io/neuralspace/ns-nlu-serve:latest
```