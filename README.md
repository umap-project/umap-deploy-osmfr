# umap-deploy-osmfr

My own scripts for deploying uMap on OSM-fr server (and the related dev server
on https://dev.umap-project.org).

## Usage

- Django settings go in settings/{FLAVOUR}.py
- remote env (for secrets) goes in default/{FLAVOUR}
- local configuration (var used when running deployement) goes in local/{FLAVOUR}

Then run, eg. for dev server
    FLAVOUR=dev make help
