#! /bin/sh
set -e

DST=/srv/umap/pgdump

sudo -u umap mkdir -p $DST
sudo -u postgres pg_dump umap | bzip2 > /tmp/umap.sql.bz2
sudo chown umap:users /tmp/umap.sql.bz2
sudo -u umap mv /tmp/umap.sql.bz2 $DST/umap.sql.bz2
