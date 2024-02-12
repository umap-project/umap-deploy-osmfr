.ONESHELL:
include .env
ifndef FLAVOUR
	FLAVOUR=staging
endif
include .env.$(FLAVOUR)
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

customize: ## Deploy uMap customization files (settings, statics, templates).
ifdef CUSTOM_SETTINGS
	rsync --checksum --rsync-path="sudo --user umap rsync" --progress --archive $(CUSTOM_SETTINGS) $(HOST):/etc/umap/umap.conf
endif
ifdef CUSTOM_STATICS
	rsync --checksum --rsync-path="sudo --user umap rsync" --progress --archive $(CUSTOM_STATICS) $(HOST):/srv/umap/theme/static
endif
ifdef CUSTOM_TEMPLATES
	rsync --checksum --rsync-path="sudo --user umap rsync" --progress --archive $(CUSTOM_TEMPLATES) $(HOST):/srv/umap/theme/templates/
endif

build/uwsgi.ini: conf/uwsgi.ini .env .env.${FLAVOUR}
	envsubst < "conf/uwsgi.ini" > "build/uwsgi.ini"

build/http.conf: conf/http.conf .env .env.${FLAVOUR}
	envsubst '$${DOMAIN}' < "conf/http.conf" > "build/http.conf"

http: build/uwsgi.ini build/http.conf ## Configure Nginx and uWsgi
	$(SUDO_RSYNC) conf/uwsgi_params $(HOST):/srv/umap/uwsgi_params
	$(SUDO_RSYNC) build/uwsgi.ini $(HOST):/etc/uwsgi/apps-enabled/umap.ini
	$(SUDO_RSYNC) conf/umap-nginx.conf $(HOST):/etc/nginx/snippets/umap.conf
	# TODO letsencrypt/certbot.
	$(SUDO_RSYNC) build/http.conf $(HOST):/etc/nginx/sites-enabled/umap
	$(WITH_SUDO) systemctl restart nginx

restart: ## Restart nginx and uwsgi.
	$(WITH_SUDO) systemctl restart uwsgi nginx

bootstrap: system db venv customize update http restart  ## Bootstrap server.

update: build/env ## Update umap python package.
	@if [[ $VERSION == git* ]]; then
		$(PIP) install ${VERSION} --upgrade
	else
		$(PIP) install umap-project==${VERSION} --upgrade
	fi
	@if [[ "$(CUSTOM_PACKAGES)" ]]; then $(PIP) install ${CUSTOM_PACKAGES}; fi
	$(CMD) collectstatic --noinput --verbosity 0
	$(CMD) migrate

deploy: update restart ## Update and restart.

build/env: SHELL := python3
build/env: .env .env.${FLAVOUR}
	from pathlib import Path
	import os
	FLAVOUR = os.environ["FLAVOUR"]
	env = dict(l.split("=", maxsplit=1) for l in Path(".env").read_text().split("\n") if l.startswith("EXPORT_"))
	flavour = dict(l.split("=", maxsplit=1) for l in Path(f".env.{FLAVOUR}").read_text().split("\n") if l.startswith("EXPORT_"))
	env.update(flavour)
	with Path("build/env").open("w") as f:
	    f.write("\n".join(f"{k}={v}" for k, v in env.items()) + "\n")
.PHONY: build/env
