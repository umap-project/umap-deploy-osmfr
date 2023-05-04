# umap-deploy

My own scripts for deploying uMap.

## Usage

- Create a `.env.flavour` file, where `flavour` is the name of your server
(`prod`, `staging`… whatever makes sense for you), that looks like:

    CUSTOM_SETTINGS=flavour.local.py
    DOMAIN=umap.server.com
    PROCESSES=4
    HOST=your.server.host.com.or.alias
    VERSION=1.2.4


Then run:
    FLAVOUR=flavour make boostrap
