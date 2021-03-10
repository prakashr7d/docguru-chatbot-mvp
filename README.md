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
