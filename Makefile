.ONESHELL:
ifndef FLAVOUR
	FLAVOUR=dev
endif
include local/$(FLAVOUR)
RUN:=ssh $(HOST)
WITH_SUDO:=$(RUN) sudo
WITH_USER:=$(RUN) sudo -u umap
WITH_POSTGRES:=$(RUN) sudo -u postgres
WITH_ENV:=$(RUN) "set -o allexport; source /srv/umap/env; set +o allexport; sudo --user umap --preserve-env"
SUDO_RSYNC=rsync --checksum --rsync-path="sudo rsync" --progress --archive
CLI:=$(RUN) "set -a; . /srv/umap/env; set +a; /srv/umap/venv/bin/umap"
VENV=/srv/umap/venv/
PIP:=$(WITH_USER) $(VENV)bin/pip
CMD:=$(WITH_USER) $(VENV)bin/umap
PROCESSES?=2  # Default value.
# Export env to child processes (eg. python scripts).
export

$(info Running with flavour "$(FLAVOUR)")

help: ## This help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help


system: ## Install system dependencies
	$(WITH_SUDO) apt update
	$(WITH_SUDO) apt install -y python3 python3-dev python3-venv wget nginx uwsgi uwsgi-plugin-python3 postgresql gcc postgis libpq-dev
	-$(WITH_SUDO) useradd -m -d /srv/umap -s /bin/bash -b /srv/ umap --system -c \"uMap System User\"
	$(WITH_SUDO) mkdir --parents /etc/umap
	$(WITH_SUDO) chown umap:users /etc/umap/

db:  ## Create the database.
	-$(WITH_POSTGRES) createuser umap
	-$(WITH_POSTGRES) createdb umap -O umap
	$(WITH_POSTGRES) psql umap -c \"CREATE EXTENSION IF NOT EXISTS postgis\"
	$(WITH_POSTGRES) psql umap -c \"CREATE EXTENSION IF NOT EXISTS unaccent\"

venv: ## Create python virtualenv.
	$(WITH_USER) python3 -m venv /srv/umap/venv
	$(PIP) install pip wheel -U

settings: ## Deploy custom settings
	$(SUDO_RSYNC) settings/$(FLAVOUR).py $(HOST):/etc/umap/umap.conf
.PHONY: settings

env: ## Deploy default env file in /srv/umap/env
	$(SUDO_RSYNC) default/$(FLAVOUR) $(HOST):/srv/umap/env
.PHONY: default

statics: ## Deploy custom statics
ifdef CUSTOM_STATICS
	$(WITH_USER) mkdir /srv/umap/theme
	rsync --checksum --rsync-path="sudo --user umap rsync" --progress --archive $(CUSTOM_STATICS) $(HOST):/srv/umap/theme/static
endif

templates: ## Deploy custom templates
ifdef CUSTOM_TEMPLATES
	$(WITH_USER) mkdir /srv/umap/theme
	rsync --checksum --rsync-path="sudo --user umap rsync" --progress --archive $(CUSTOM_TEMPLATES) $(HOST):/srv/umap/theme/templates/
endif

customize: settings statics templates ## Deploy uMap customization files (settings, statics, templates).

build/uwsgi.ini: conf/uwsgi.ini local/${FLAVOUR}
	envsubst < "conf/uwsgi.ini" > "build/uwsgi.ini"

build/http.conf: conf/http.conf local/${FLAVOUR}
	envsubst '$${DOMAIN}' < "conf/http.conf" > "build/http.conf"

build/https.conf: conf/https.conf local/${FLAVOUR}
	envsubst '$${DOMAIN}' < "conf/https.conf" > "build/https.conf"

http: build/uwsgi.ini build/http.conf build/https.conf ## Configure Nginx and uWsgi
	$(SUDO_RSYNC) conf/uwsgi_params $(HOST):/srv/umap/uwsgi_params
	$(SUDO_RSYNC) build/uwsgi.ini $(HOST):/etc/uwsgi/apps-enabled/umap.ini
	$(SUDO_RSYNC) conf/umap-nginx.conf $(HOST):/etc/nginx/snippets/umap.conf
	# In OSM France server, https is not handle in the VM but in a global proxy
ifeq ($(HTTPS), 1)
	$(SUDO_RSYNC) build/https.conf $(HOST):/etc/nginx/sites-enabled/umap
else
	$(SUDO_RSYNC) build/http.conf $(HOST):/etc/nginx/sites-enabled/umap
endif
	$(WITH_SUDO) systemctl restart nginx

restart: ## Restart nginx and uwsgi.
	$(WITH_SUDO) systemctl restart uwsgi nginx

bootstrap: system db venv customize update http restart  ## Bootstrap server.

update: ## Update umap python package and deps.
	@if [[ $VERSION == git* ]]; then
		$(PIP) install ${VERSION} --upgrade
	else
		$(PIP) install umap-project==${VERSION} --upgrade
	fi
	@if [[ "$(CUSTOM_PACKAGES)" ]]; then $(PIP) install ${CUSTOM_PACKAGES}; fi
	$(CMD) collectstatic --noinput --verbosity 0
	$(CMD) migrate

deploy: update restart ## Update and restart.
