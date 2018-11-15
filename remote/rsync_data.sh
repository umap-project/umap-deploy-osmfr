#! /bin/bash

# WARNING this script is to be used on the SLAVE host.

sudo -u umap rsync --archive --update --verbose --exclude='*.gz' --bwlimit=5000 $${host}:/srv/umap/media_root/ /srv/umap/media_root/
sudo -u umap rsync --archive --update --verbose --bwlimit=5000 $${host}:/srv/umap/pgdump/ /srv/umap/pgdump/
