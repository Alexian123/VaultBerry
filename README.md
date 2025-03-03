# VaultBerry - Backend

## Deployment

### Repository

Clone the [VaultBerry repository](https://github.com/Alexian123/VaultBerry).

### Dependencies

- Install [Docker](https://www.docker.com/).

- Install [Docker Compose](https://docs.docker.com/compose/).

### Environment

Create the **.env** file in the root of the project with your environment preferences, or use the following example (NOT FOR PRODUCTION!):

```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=database

DB_HOST=db
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DB_HOST}/${POSTGRES_DB}
SECRET_KEY=mysecretkey

FLASK_APP=run:app
FLASK_ENV=development
FLASK_DEBUG=1

ADMIN_EMAIL=admin@example.com       # email for the admin user
ADMIN_PASSWORD=admin                # password for the admin user

MAIL_SERVER=<mail_server>   # example: smtp.gmail.com
MAIL_USERNAME=<your_email_address>
MAIL_PASSWORD=<your_email_password>
```

### Build

Create the containers:

```sh
docker-compose up --build
```

Upgrade database migrations:
```sh
docker-compose exec web flask db upgrade
```

### Container management

Stop the containers:
```sh
docker-compose down
```

Start the containers:
```sh
docker-compose up
```

## Unit Tests

### Dependencies

- Install [Python](https://www.python.org/) and [pip](https://pypi.org/project/pip/).

- Install [venv](https://docs.python.org/3/library/venv.html).

### Environment

Create a virtual environemnt (venv) in the root of the project:

```sh
python -m venv venv
```

Activate the venv in the current shell:

```sh
source venv/bin/activate
```

Install the required packages with pip:

```sh
pip install --no-cache-dir -r requirements.txt
```

### Running tests

> New test cases must be placed inside the **tests** directory and the names of the test files must start with "test_".

Use the **run_tests.sh** script to run all properly defined test cases:

```sh
sh run_tests.sh
```

