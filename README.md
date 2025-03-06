# VaultBerry - Backend

## API Endpoints

> Return body for failed requests: ```{"error": "some error message"}```

| Name             | Method | Route                     | Request Args   | Request Body | Success Code | Error Code(s) | Successful Return Body | 
| :--------------- | :----: | :------------------------ | :------------- | :----------- | :----------: | :-----------: | :--------------------- |
| Register         | POST   | /register                 | -              | ```{```<br>&nbsp;&nbsp;```"account": {```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"email": "test@email.com"```<br>&nbsp;&nbsp;```},```<br>&nbsp;&nbsp;```"keychain": {```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"salt": "abcdefghabcdefghabcdefgh",```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"vault_key": "test key",```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"recovery_key": "test recovery key"```<br>&nbsp;&nbsp;```},```<br>&nbsp;&nbsp;```"password": "test"```<br>```}``` | 201 | 400 | ```{"message": "User registered successfully"}``` |
| Login            | POST   | /login                    | -              | ```{```<br>&nbsp;&nbsp;```"email": "test@email.com",```<br>&nbsp;&nbsp;```"password": "test"```<br>```}``` | 200 | 400, 401 | ```{```<br>&nbsp;&nbsp;```"salt": "abcdefghabcdefghabcdefgh",```<br>&nbsp;&nbsp;```"vault_key": "test key",```<br>&nbsp;&nbsp;```"recovery_key": "test recovery key"```<br>```}``` |
| Logout           | POST   | /logout                   | -              | - | 200 | 400 | ```{"message": "Logout successful"}``` |
| GetRecoveryOTP   | GET    | /recovery                 | email (String) | - | 200 | 400, 401 | ```{"message": "OTP sent successfully"}``` |
| RecoveryLogin    | POST   | /recovery                 | -              | ```{```<br>&nbsp;&nbsp;```"email": "test@email.com",```<br>&nbsp;&nbsp;```"password": "123456789"```<br>```}``` | 200 | 400, 401 | ```{```<br>&nbsp;&nbsp;```"salt": "abcdefghabcdefghabcdefgh",```<br>&nbsp;&nbsp;```"vault_key": "test key",```<br>&nbsp;&nbsp;```"recovery_key": "test recovery key"```<br>```}``` |
| GetAccount       | GET    | /account                  | -              | - | 200 | 400 | ```{```<br>&nbsp;&nbsp;```"email": "example@email.com",```<br>&nbsp;&nbsp;```"first_name": "John",```<br>&nbsp;&nbsp;```"last_name": "Doe"```<br>```}``` |
| UpdateAccount    | PUT    | /account                  | -              | ```{```<br>&nbsp;&nbsp;```"email": "example@email.com",```<br>&nbsp;&nbsp;```"first_name": "John",```<br>&nbsp;&nbsp;```"last_name": "Doe"```<br>```}``` | 201 | 400 | ```{"message": "Account updated successfully"}```|
| DeleteAccount    | DELETE | /account                  | -              | - | 201 | 400, 500 | ```{"message": "Account deleted successfully"}``` |
| ChangePassword   | PUT    | /account/password         | -              | ```{"password": "test"}``` | 201 | 400 | ```{"message": "Password changed successfully"}``` |
| UpdateKeyChain   | PUT    | /account/keychain         | -              | ```{```<br>&nbsp;&nbsp;```"salt": "abcdefghabcdefghabcdefgh",```<br>&nbsp;&nbsp;```"vault_key": "test key",```<br>&nbsp;&nbsp;```"recovery_key": "test recovery key"```<br>```}``` | 201 | 400 | ```{"message": "Keychain updated successfully"}``` |
| GetVaultEntries  | GET    | /entries                  | -              | - | 200 | 500 | ```[```<br>&nbsp;&nbsp;```{```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"timestamp": 15188,```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"title": "Account 1",```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"url": "www.website.com",```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"encrypted_username": "cvnuruw3r35df!@$5",```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"encrypted_password": "-05=?>2tglov",```<br>&nbsp;&nbsp;&nbsp;&nbsp;```"notes": "lorem ipsum"```<br>&nbsp;&nbsp;```},```<br>&nbsp;&nbsp;```...```<br>```]``` |
| AddVaultEntry    | POST   | /entries                  | -              | ```{```<br>&nbsp;&nbsp;```"timestamp": 15188,```<br>&nbsp;&nbsp;```"title": "Account 1",```<br>&nbsp;&nbsp;```"url": "www.website.com",```<br>&nbsp;&nbsp;```"encrypted_username": "cvnuruw3r35df!@$5",```<br>&nbsp;&nbsp;```"encrypted_password": "-05=?>2tglov",```<br>&nbsp;&nbsp;```"notes": "lorem ipsum"```<br>```}``` | 201 | 400, 500 | ```{"message": "Entry added successfully"}``` |
| UpdateVaultEntry | PUT    | /entries                  | -              | ```{```<br>&nbsp;&nbsp;```"timestamp": 15188,```<br>&nbsp;&nbsp;```"title": "Account 1",```<br>&nbsp;&nbsp;```"url": "www.website.com",```<br>&nbsp;&nbsp;```"encrypted_username": "cvnuruw3r35df!@$5",```<br>&nbsp;&nbsp;```"encrypted_password": "-05=?>2tglov",```<br>&nbsp;&nbsp;```"notes": "lorem ipsum"```<br>```}``` | 201 | 400, 500 | ```{"message": "Entry updated successfully"}``` |
| DeleteVaultEntry | DELETE | /entries/\<int:timestamp> | -              | - | 201 | 400, 500 | ```{"message": "Entry deleted successfully"}``` |

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

