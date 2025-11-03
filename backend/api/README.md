# TEMPLATE API REST PYTHON - FLASK

This project contains the template for API REST developed using Python with Flask framework and a MongoDB database.

## General dependences

- Python
- Flask
- MongoDB

## Environment variables

For a correct operation of the REST API it will be necessary to generate a .env file where to include the environment variables.

There is an example file with the name .env.example where these variables are shown, an is the following:

```bash
# Flask
FLASK_APP=api.py
FLASK_CONFIG=development
FLASK_ENV=development

# Database
MONGODB_HOST=mongodb://localhost/database
MONGODB_PORT=27017
MONGODB_DATABASE=database
MONGODB_USERNAME=username
MONGODB_PASSWORD=password
```
- FLASK_APP: is used to specify how to load the application if "flask" command is installed. 

- FLASK_CONFIG: it allows you to indicate what configuration is loaded when API REST is started. The options can be **development**, **production** or **testing**.

- FLASK_ENV: specifies the environment where the API REST will be launched.

- MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE, MONGODB_USERNAME, MONGODB_PASSWORD: 
are the variables that are necessary to make the connection to the DB.

## Setup

This section details the steps to follow for the correct installation of the API REST.

1. Create virtual environment:

```bash
$ python3 -m venv env
```

2. Activate environment:

```bash
$ source env/bin/activate
```

2. Upgrade pip:

```bash
$ pip install --upgrade pip
```

3. Install wheel:

```bash
$ pip install wheel
```

4. Install project dependencies for development:

```bash
$ pip install -r requirements/dev.txt
```

## Run

To launch the API REST, you just have to launch the following command:

```bash
$ python api.py
```

## Run tests

Unit tests are implemented for the defined endpoints. In order to launch these tests, the DB must be available and launch the following command:

```bash
$ pytest -v
```

## Coverage

To check the coverage of the tests performed, the following command must be executed:

```bash
$ coverage run -m pytest
$ coverage html
```

To see the coverage in a more elegant way we can execute the following command:

```bash
$ coverage html
```

An htmlcov directory will be generated. In it we can see an index.hml that contains the coverage of the project.

## MongoEngine intellisense

Currently VSCode does not have support for Mongoengine so intellisense does not work and returns errors. To avoid this, it is possible to indicate the following in the settings:

```bash
"python.linting.pylintArgs": [
	"--load-plugins=pylint_mongoengine", "--errors-only"
],
```
