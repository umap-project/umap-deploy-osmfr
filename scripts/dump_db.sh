#! /bin/sh
set -e

DST=/srv/umap/pgdump
MONTHDAY=$(date +"%d")

sudo -u umap mkdir -p $DST
sudo -u postgres pg_dump umap | bzip2 > /tmp/umap.sql.bz2
sudo chown umap:users /tmp/umap.sql.bz2
sudo -u umap mv /tmp/umap.sql.bz2 $DST/umap.$MONTHDAY.sql.bz2
sudo -u umap ln -sf $DST/umap.$MONTHDAY.sql.bz2 $DST/umap.latest.sql.bz2
