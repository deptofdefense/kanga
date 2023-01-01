# Kanga

## Description

Kanga is an open source Python application for sending messages to SMS and [WhatsApp](https://www.whatsapp.com/) targets using the [Twilio](https://www.twilio.com/) API.

For information about the Twilio Python library see [The Twilio Python Helper Library](https://www.twilio.com/docs/libraries/python).

## Development

Kanga is built on the widely used [Django](https://www.djangoproject.com/) framework, so the development workflow should be familiar to most Django developers.

### Setup

The first step to develop the application is to create a Python virtual environment.  You can use the following commands to create the virtual environment using [venv](https://docs.python.org/3/library/venv.html), activate the environment, install all the required dependencies, and install the application as editable.

Run these commands individually.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install build
pip install flake8
pip install wheel
pip install -e .
```

If using `macOS` install these dependencies if they are missing:

```shell
brew install awscli chamber circleci direnv jq libpq python@3.9
```

See `.envrc.local.template` for instructions on setting up local environment variables.

### Basic Workflow

First, build the database container using:

```shell
make docker_build_db
```

Second, build the application container using:

```shell
make docker_build_app
```

Next, start the database in the background using:

```shell
make docker_start_db
```

To reset the application run:

```sh
# if the virtual environment is not active, then activate it
source .venv/bin/activate
make reset
```

To launch the server run:

```sh
# if the virtual environment is not active, then activate it
source .venv/bin/activate
make runserver
```

To view the website go to:

http://kangalocal:8080/

### Using Docker Compose

You can use docker compose to test the application using HTTPS and client certificates.

Using docker compose requires the "web" container, which can be built using:

```shell
make docker_build_web
```

Add the following to `/etc/hosts`:

```
127.0.0.1 kangalocal
```

Create the certificate authority, server key pair, and client key pair.

```shell
make temp/ca.crt temp/server.crt temp/DoDRoots.crt temp/client.p12
```

Then launch the docker cluster using:

```shell
make up
```

Then, collect the Django static files in Docker using:

```shell
make docker_run_collectstatic
````

To view the website go to:

https://kangalocal:8443/


### Migrations

To build migrations for changes to database models use the following.

```
make migrations
```

To apply migrations use the following.

```
make migrate
```

## Deployment

### Production

These are the current steps:

```sh
ssh kanga
cd /home/ubuntu/kanga
git pull
make docker_build_app docker_build_web
make sync-secrets-vars
source app-kanga-prod.vars
make up-prod
make prod-collectstatic
```

## Contributing

No resources are currently dedicated toward improving this application.  We'd love to have your contributions!  Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more info.

## Known Issues

The local Docker Compose deployment of Kanga does not have CSRF validation properly configured, which leads to the following errors: "CSRF verification failed. Request aborted."

## Security

This software is a prototype and provided as open source software without any guarantee of security.  No resources are currently dedicated to improving the security of this software, but we will strongly consider any patches or suggestions.

Please see [SECURITY.md](SECURITY.md) for more info.

## License

This project constitutes a work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.  However, because the project utilizes code licensed from contributors and other third parties, it therefore is licensed under the MIT License.  See LICENSE file for more information.
test
test
