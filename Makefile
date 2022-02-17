.PHONY: help
help:  ## Print the help documentation
	@grep -E '^[\/a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#
# Python
#

.PHONY: flake8
flake8:  ## install Python requirements
	python3 -m flake8 kanga

.PHONY: requirements
requirements:  ## install Python requirements
	pip3 install -r requirements.txt

.PHONY: editable
editable:  ## install this repo as editable
	pip3 install -e .

temp/secretkey:  ## create a secret key
	mkdir -p temp
	@openssl rand -hex 64 | tee temp/secretkey

#
# Docker Containers
#

.PHONY: docker_start
docker_start:  ## start docker
	open --background -a Docker 2> /dev/null

.PHONY: docker_build_db
docker_build_db: ## build database container
	scripts/docker-build-db "docker/postgis" "kanga-db"

.PHONY: docker_stop_db
docker_stop_db: ## stop database container
	@scripts/docker-stop-db "kanga-db"

.PHONY: docker_start_db
docker_start_db: ## start database container
	@scripts/docker-start-db "kanga-db:latest" "kanga-db"

.PHONY: docker_shell_db
docker_shell_db: docker_start_db ## open shell into database container
	docker exec -it kanga-db bash

.PHONY: docker_build_app
docker_build_app: bin/rds-ca-2019-root.pem bin_linux/chamber ## build app container
	scripts/docker-build-app "docker/kanga/gunicorn" "kanga-app"

.PHONY: docker_build_web
docker_build_web: temp/ca.crt temp/server.crt temp/DoDRoots.crt ## build app container
	scripts/docker-build-web "docker/nginx" "kanga-web"

.PHONY: docker_start_web
docker_start_web: temp/client.crt ## start web container
	@scripts/docker-start-web "kanga-web:latest" "kanga-web"

.PHONY: docker_shell_web
docker_shell_web: docker_start_web ## open shell into web container
	docker exec -it kanga-web /bin/bash

.PHONY: docker_run_collectstatic
docker_run_collectstatic: ## Collect static files for docker
	docker-compose -f docker-compose.yml exec app python manage.py collectstatic


.PHONY: up
up: ## Run docker-compose for dev
	docker-compose up -d db
	sleep 5s
	docker-compose up -d app
	docker-compose up -d web

.PHONY: down
down: ## Stop containers for docker compose
	docker-compose down

#
# Prod Targets
#

.PHONY: up-prod
up-prod: sync-secrets sync-prod-data ## Run docker-compose containers for prod
	docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

.PHONY: down-prod
down-prod: ## Destroy the docker-compose containers for prod
	docker-compose -f docker-compose.prod.yml down

.PHONY: stop-prod
stop-prod: ## Stop the docker-compose containers for prod
	docker-compose -f docker-compose.prod.yml stop

.PHONY: start-prod-app
start-prod-app: .env.prod ## Start prod app
	docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d app

.PHONY: stop-prod-app
stop-prod-app: .env.prod ## Stop prod app
	docker-compose --env-file .env.prod -f docker-compose.prod.yml stop app

.PHONY: restart-prod-app
restart-prod-app: .env.prod stop-prod-app start-prod-app ## Restart prod app

.PHONY: start-prod-web
start-prod-web: .env.prod ## Start prod web
	docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d web

.PHONY: stop-prod-web
stop-prod-web: .env.prod ## Stop prod web
	docker-compose --env-file .env.prod -f docker-compose.prod.yml stop web

.PHONY: restart-prod-web
restart-prod-web: .env.prod stop-prod-web start-prod-web ## Restart prod web

# The .env file for docker-compose can't have the word 'export' and doesn't handle any quotation marks
# This means putting quotations into a value can be brittle
.PHONY: sync-secrets
sync-secrets: ## Sync secrets from SSM to .env.prod file
	chamber env app-kanga-prod | sed "s/export //g" | sed "s/'//g" | sort > .env.prod

.env.prod: ## Create an .env.prod file, used for other targets
	chamber env app-kanga-prod | sed "s/export //g" | sed "s/'//g" | sort > .env.prod

.PHONY: sync-secrets-vars
sync-secrets-vars: ## Sync secrets from SSM to app-kanga-prod.vars file to source into environment
	echo "#!/bin/bash" > app-kanga-prod.vars
	chamber env app-kanga-prod >> app-kanga-prod.vars
	echo "Now run 'source app-kanga-prod.vars' to get env vars installed"

.PHONY: sync-prod-data
sync-prod-data: ## Sync prod data from S3 to host
	[ -n "$(FIXTURE_BUCKET)" ] && aws s3 sync s3://$(FIXTURE_BUCKET)/ /home/ubuntu/kanga/data/
	[ -n "$(TLS_BUCKET)" ] && aws s3 sync s3://$(TLS_BUCKET)/ /home/ubuntu/tls/

.PHONY: prod-manage
prod-manage: .env.prod ## Run the manage.py command
	docker-compose -f docker-compose.prod.yml --env-file .env.prod exec app python manage.py

.PHONY: prod-collectstatic
prod-collectstatic: .env.prod ## Collect static files for prod
	docker-compose -f docker-compose.prod.yml --env-file .env.prod exec app python manage.py collectstatic

.PHONY: prod-createsuperuser
prod-createsuperuser: ## Create prod superuser
	docker-compose -f docker-compose.prod.yml --env-file .env.prod exec app python manage.py createsuperuser --username admin --email admin@kanga.dds.mil

.PHONY: prod-migrate
prod-migrate: .env.prod docker_build_app stop-prod start-prod-app ## Migrate the database for prod
	docker-compose -f docker-compose.prod.yml --env-file .env.prod exec app python manage.py migrate
	docker-compose -f docker-compose.prod.yml --env-file .env.prod start web

.PHONY: prod-db-dump
prod-db-dump: ## Dump the DB
	pg_dump -d $(DB_NAME) -h $(DB_HOST) -U $(DB_USER) -W > dump_$(date --rfc-3339=seconds | sed 's/ /T/').sql

.PHONY: prod-psql
prod-psql: ## Dump the DB
	psql -d $(DB_NAME) -h $(DB_HOST) -U $(DB_USER)

#
# Django Targets
#

.PHONY: collectstatic
collectstatic: ## collect static files
	python3 manage.py collectstatic

.PHONY: migrations
migrations: ## make migrations
	python3 manage.py makemigrations kanga

.PHONY: migrate
migrate: docker_start_db  ## migrate database
	python3 manage.py migrate

.PHONY: runserver
runserver: temp/secretkey ## run server
	python3 manage.py runserver 0.0.0.0:${APP_PORT}

.PHONY:
superuser:
	@echo "Password"
	@openssl rand -hex 8
	python3 manage.py createsuperuser --username admin --email admin@kanga.dds.mil

#
# Database Targets
#

.PHONY: psql
psql:
	scripts/psql-wrapper

.PHONY: db_reset
db_reset:
	DB_NAME=postgres scripts/psql-wrapper 'DROP DATABASE kanga;'
	DB_NAME=postgres scripts/psql-wrapper 'CREATE DATABASE kanga;'
	make migrate

#
# Docker Targets
#

.PHONY: prune_images
prune_images:  ## Prune docker images
	@echo '****************'
	docker image prune -a

.PHONY: prune_containers
prune_containers:  ## Prune docker containers
	@echo '****************'
	docker container prune

.PHONY: prune_volumes
prune_volumes:  ## Prune docker volumes
	@echo '****************'
	docker volume prune

.PHONY: prune
prune: prune_images prune_containers prune_volumes ## Prune docker containers, images, and volumes


#
# Certificate Targets
#

bin/rds-ca-2019-root.pem:
	mkdir -p bin/
	curl -sSo bin/rds-ca-2019-root.pem https://s3.amazonaws.com/rds-downloads/rds-ca-2019-root.pem

temp/ca.crt:
	mkdir -p temp
	openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 -subj "/C=US/O=Atlantis/OU=Atlantis Digital Service/CN=kangaca" -keyout temp/ca.key -out temp/ca.crt

temp/ca.srl:
	echo '01' > temp/ca.srl

temp/index.txt:
	touch temp/index.txt

temp/index.txt.attr:
	echo 'unique_subject = yes' > temp/index.txt.attr

temp/ca.crl.pem: temp/ca.crt temp/index.txt temp/index.txt.attr
	openssl ca -batch -gencrl -config conf/openssl.cnf -out temp/ca.crl.pem

temp/ca.crl.der: temp/ca.crl.pem
	openssl crl -in temp/ca.crl.pem -outform DER -out temp/ca.crl.der

temp/server.crt: temp/ca.crt temp/ca.srl temp/index.txt temp/index.txt.attr
	openssl genrsa -out temp/server.key 2048
	openssl req -new -config conf/openssl.cnf -key temp/server.key -subj "/C=US/O=Atlantis/OU=Atlantis Digital Service/CN=kangalocal" -out temp/server.csr
	openssl ca -batch -config conf/openssl.cnf -extensions server_ext -notext -in temp/server.csr -out temp/server.crt

temp/client.crt: temp/ca.crt temp/ca.srl temp/index.txt temp/index.txt.attr
	mkdir -p temp
	openssl genrsa -out temp/client.key 2048
	openssl req -new -key temp/client.key -subj "/C=US/O=Atlantis/OU=Atlantis Digital Service/OU=CONTRACTOR/CN=LAST.FIRST.MIDDLE.ID" -out temp/client.csr
	openssl ca -batch -config conf/openssl.cnf -extensions client_ext -notext -in temp/client.csr -out temp/client.crt

temp/client.p12: temp/ca.crt temp/client.crt
	mkdir -p temp
	openssl pkcs12 -export -out temp/client.p12 -inkey temp/client.key -in temp/client.crt -certfile temp/ca.crt -passout pass:

.PHONY: crl
crl:  ## Create the Certificate Revocation List
	rm -f temp/ca.crl.pem temp/ca.crl.der
	make temp/ca.crl.der

.PHONY: crl_revoke_client
crl_revoke_client:  ## Revoke client certificate with CRL
	openssl ca -batch -config conf/openssl.cnf -cert temp/ca.crt -keyfile temp/ca.key -revoke temp/client.crt

# See https://public.cyber.mil/pki-pke/pkipke-document-library/?_dl_facet_pkipke_type=popular-dod-certs
# for instructions on how to obtain DoD PKI certs -- which are *not*
# CAC-firewalled. The ZIP file they link you to includes the raw DoD Root certs
# in various formats.

# File name format *inside* the ZIP file
ROOT_CERTS := Certificates_PKCS7_v5.9_DoD

# Current versions of the DoD PKI distro contain all the certs in a pkcs7 bundle,
# which NGINX doesn't handle natively, but is not too difficult to have openssl
# convert into a bunch of concatenated individual PEM-format certs.
temp/DoDRoots.crt: ## Convert DoD Root certs to pem
	mkdir -p temp
	openssl pkcs7 -in "DoDCerts/$(ROOT_CERTS).pem.p7b" -print_certs -out "$@"

download_dod_certs: ## Download the DoD Root Certs, probably won't work except in browser
	curl -s -o "$(ROOT_CERTS).zip" "https://dl.dod.cyber.mil/wp-content/uploads/pki-pke/zip/$(ROOT_CERTS).zip"

#
# Tools
#

bin_linux/chamber:
	mkdir -p bin_linux
	curl -LsSo bin_linux/chamber https://github.com/segmentio/chamber/releases/download/v2.10.1/chamber-v2.10.1-linux-amd64
	chmod 755 bin_linux/chamber

#
# Kanga Target
#

#
# Python
#

.PHONY: reset
reset:  ## install Python requirements
	scripts/kanga-reset


#
# Clean Targets
#

clean:
	rm -fr bin
	rm -fr temp
	rm -fr *.egg-info
	rm -fr docker/*/temp/
