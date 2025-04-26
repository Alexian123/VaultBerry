# VaultBerry - Backend

Official client: [VaultBerry App](https://github.com/Alexian123/VaultBerryApp)

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

FERNET_KEY=<encryption_key>         # Generate once using app.utils.security_utils.SecurityManager.generate_fernet_key()
KDF_SECRET=<key_derivation_secret>  # Generate once using app.utils.security_utils.SecurityManager.generate_kdf_secret()
```

### Build

-Generate SSL certificate:
```sh
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/CN=192.168.1.131" -addext "subjectAltName = IP:192.168.1.131"
```

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

### Running inside WSL

Add inbound rule to Windows Defender Firewall to allow all incoming connections on port 8443

Run the following command in PowerShell with *connectaddress* set to the IP addres of the WSL machine:
```sh
netsh interface portproxy add v4tov4 listenport=8443 listenaddress=0.0.0.0 connectport=8443 connectaddress=192.168.90.206
```

Command to disable port proxy:
```sh
netsh interface portproxy delete v4tov4 listenport=8443 listenaddress=0.0.0.0
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

## API Endpoints

> Return body for failed requests: ```{"error": "some error message"}```

| Name              | Login Required | Method | Route                      | Args        | Request Body                                                                                                                                                                                                                                                 | Success Code | Error Code(s)           | Successful Return Body                                                                                                                                                |
|-------------------|----------------|--------|----------------------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Register          | NO             | POST   | /register                  | -           | ``` { "account": { "email": <str>, "first_name": <str?>, "last_name": <str?> }, "passwords": { "regular_password": <str>, "recovery_password": <str>, }, "keychain": { "salt": <base64_str>, "vault_key": <base64_str>, "recovery_key": <base64_str> } } ``` | 201          | 500, 400, 409           | ```{"message": "User registered successfully"}```                                                                                                                     |
| LoginStep1        | NO             | POST   | /login/step1               | -           | ``` { "email": <str>, "client_message": <str> "code": <str?> } ```                                                                                                                                                                                           | 200          | 500, 400, 401, 403, 404 | ```{"server_message": <str>}```                                                                                                                                       |
| LoginStep2        | NO             | POST   | /login/step2               | -           | ``` { "email": <str>, "client_message": <str> } ```                                                                                                                                                                                                          | 200          | 500, 401, 403, 404      | ``` { "server_message": <str>, "keychain": { "salt": <base64_str>, "vault_key": <base64_str>, "recovery_key": <base64_str> } } ```                                    |
| Logout            | NO             | POST   | /logout                    | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 401                | ```{"message": "Logout successful"}```                                                                                                                                |
| RecoverySend      | NO             | POST   | /recovery/send             | email (str) | -                                                                                                                                                                                                                                                            | 200          | 500, 400, 401 404       | ```{"message": "OTP sent successfully"}```                                                                                                                            |
| RecoveryLogin     | NO             | POST   | /recovery/login            | -           | ``` { "email": <str>, "recovery_password": <str>, "otp": <str> } ```                                                                                                                                                                                         | 200          | 500, 401, 404           | ``` { "keychain": { "salt": <base64_str>, "vault_key": <base64_str>, "recovery_key": <base64_str> } } ```                                                             |
| GetAccountInfo    | YES            | GET    | /account                   | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 401                | ``` { "account": { "email": <str>, "first_name": <str?>, "last_name": <str?> } } ```                                                                                  |
| UpdateAccountInfo | YES            | PATCH  | /account                   | -           | ``` { "account": { "email": <str>, "first_name": <str?>, "last_name": <str?> } } ```                                                                                                                                                                         | 200          | 500, 401, 409           | ```{"message": "Account info updated successfully"}```                                                                                                                |
| DeleteAccount     | YES            | DELETE | /account                   | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 401, 403           | ```{"message": "Account deleted successfully"}```                                                                                                                     |
| ChangePassword    | YES            | PATCH  | /account/password          | -           | ``` { "passwords": { "regular_password": <str>, "recovery_password": <str>, }, "keychain": { "salt": <base64_str>, "vault_key": <base64_str>, "recovery_key": <base64_str> } } ```                                                                           | 200          | 500, 401                | ```{"message": "Password changed successfully"}```                                                                                                                    |
| Setup2FA          | YES            | POST   | /account/2fa/setup         | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 400, 401           | ``` { "provisioning_uri": <str>, "qrcode": <str> } ```                                                                                                                |
| Get2FAStatus      | YES            | GET    | /account/2fa/status        | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 401                | ```{"enabled": <bool>}```                                                                                                                                             |
| Disable2FA        | YES            | POST   | /account/2fa/disable       | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 400, 401           | ```{"message": "2FA disabled successfully"}```                                                                                                                        |
| GetVaultEntries   | YES            | GET    | /entries                   | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 401                | ``` [ { "timestamp": <big_int>, "title": <str>, "url": <str?>, "encrypted_username": <base64_str?>, "encrypted_password": <base64_str?>, "notes": <str?> }, ... ] ``` |
| AddVaultEntry     | YES            | POST   | /entries                   | -           | ``` { "timestamp": <big_int>, "title": <str>, "url": <str?>, "encrypted_username": <base64_str?>, "encrypted_password": <base64_str?>, "notes": <str?> } ```                                                                                                 | 201          | 500, 401, 409           | ```{"message": "Entry added successfully"```                                                                                                                          |
| UpdateVaultEntry  | YES            | PATCH  | /entries                   | -           | ``` { "timestamp": <big_int>, "title": <str>, "url": <str?>, "encrypted_username": <base64_str?>, "encrypted_password": <base64_str?>, "notes": <str?> } ```                                                                                                 | 200          | 500, 401, 404           | ```{"message": "Entry updated successfully"}```                                                                                                                       |
| DeleteVaultEntry  | YES            | DELETE | /entries/\<int:timestamp\> | -           | -                                                                                                                                                                                                                                                            | 200          | 500, 401, 404           | ```{"message": "Entry deleted successfully"}```                                                                                                                       |

## Admin Control Dashboard

> Work in progress

Access route **/admin/login** from your browser to login with the admin account (automatically created on the first run).
<br>
At the moment, you can view the content of each table from the database.
