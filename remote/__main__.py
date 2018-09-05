import minicli
from usine import (chown, config, connect, exists, mkdir, put, run, sudo,
                   template)


@minicli.cli
def umap_cmd(cmd):
    with sudo(user='umap'):
        run('/srv/umap/venv/bin/umap {}'.format(cmd))


@minicli.cli
def pip(cmd):
    with sudo(user='umap'):
        run('/srv/umap/venv/bin/pip {}'.format(cmd))


@minicli.cli
def system():
    with sudo():
        run('apt update')
        run('apt install -y python3 python3-dev python3-venv '
            'wget nginx uwsgi uwsgi-plugin-python3 postgresql gcc postgis')
        # https://bugs.launchpad.net/ubuntu/+source/python3.6/+bug/1768644
        run('apt install -y dpkg-dev')
        mkdir('/srv/umap')
        mkdir('/etc/umap')
        run('useradd -N umap -d /srv/umap/ || exit 0')
        chown('umap:users', '/srv/umap/', recursive=False)
        chown('umap:users', '/etc/umap/')
        run('chsh -s /bin/bash umap')


@minicli.cli
def db():
    with sudo(user='postgres'):
        run('createuser umap || exit 0')
        run('createdb umap -O umap || exit 0')
        run('psql umap -c "CREATE EXTENSION IF NOT EXISTS postgis"')
        run('psql umap -c "CREATE EXTENSION IF NOT EXISTS unaccent"')


@minicli.cli
def venv():
    with sudo(user='umap'):
        run('python3 -m venv /srv/umap/venv')
    pip('install pip -U')


@minicli.cli
def customize():
    if not config.custom:
        return
    with sudo(user='umap'):
        if config.custom.settings:
            put(config.custom.settings, '/etc/umap/umap.conf')
        if config.custom.static:
            put(config.custom.static, '/srv/umap/theme/static')
        if config.custom.templates:
            put(config.custom.templates, '/srv/umap/theme/templates')


@minicli.cli
def http():
    """Configure Nginx and letsencrypt."""
    with sudo():
        put('remote/uwsgi_params', '/srv/umap/uwsgi_params')
        uwsgi_conf = template('remote/uwsgi.ini',
                              processes=config.processes or 4)
        put(uwsgi_conf, '/etc/uwsgi/apps-enabled/umap.ini')
        put('remote/umap-nginx.conf', '/etc/nginx/snippets/umap.conf')
        put('remote/letsencrypt.conf', '/etc/nginx/snippets/letsencrypt.conf')
        put('remote/ssl.conf', '/etc/nginx/snippets/ssl.conf')
        pempath = f'/etc/letsencrypt/live/{config.domain}/fullchain.pem'
        if exists(pempath):
            print(f'{pempath} found, using https configuration')
            conf = template('remote/https.conf', **config)
        else:
            print(f'{pempath} not found, using http configuration')
            # Before letsencrypt.
            conf = template('remote/http.conf', **config)
        put(conf, '/etc/nginx/sites-enabled/umap')
        restart('nginx')


@minicli.cli
def letsencrypt():
    """Configure letsencrypt."""
    with sudo():
        run('add-apt-repository --yes ppa:certbot/certbot')
        run('apt update')
        run('apt install -y certbot')
    mkdir('/var/www/letsencrypt/.well-known/acme-challenge')
    certbot_conf = template('remote/certbot.ini', domain=config.domain)
    put(certbot_conf, '/var/www/certbot.ini')
    run('certbot certonly -c /var/www/certbot.ini --non-interactive '
        '--agree-tos')


@minicli.cli
def bootstrap():
    system()
    db()
    venv()
    customize()
    http()
    deploy()


def write_default():
    content = '\n'.join(['{}={}'.format(k, v)
                         for k, v in config.get('env', {}).items()])
    with sudo():
        run('echo "{}" | tee /etc/default/umap'.format(content))


@minicli.cli
def deploy():
    pip(f'install umap-project=={config.version} --upgrade')
    if config.extra_packages:
        pip('install {} --upgrade'.format(' '.join(config.extra_packages)))
    umap_cmd('migrate')
    umap_cmd('collectstatic --noinput --verbosity 0')
    # Compress even if COMPRESS_ENABLED=False in local.py.
    umap_cmd('compress --force')
    write_default()
    restart()


@minicli.cli
def restart(*services):
    with sudo():
        if not services:
            services = ['uwsgi', 'nginx']
        systemctl('restart {}'.format(' '.join(services)))


@minicli.cli
def systemctl(*cmd):
    run('systemctl {}'.format(' '.join(cmd)))


@minicli.cli
def install_db_dump():
    """
    Write a daily script to dump the database.
    """
    put('remote/dump_db.sh', '/etc/cron.daily/dump_umap_db')
    run('chmod +x /etc/cron.daily/dump_umap_db')


@minicli.wrap
def wrapper(hostname, configpath):
    with connect(hostname=hostname, configpath=configpath):
        yield


if __name__ == '__main__':
    minicli.run(hostname='umap.dev', configpath='config.yml')
