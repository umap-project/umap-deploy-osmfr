#! /bin/sh
set -e

set -a
. /srv/umap/env
set +a
sudo --preserve-env --user umap /srv/umap/venv/bin/umap empty_trash
