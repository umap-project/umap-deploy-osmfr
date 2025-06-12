from email.utils import getaddresses

from umap.settings.base import *  # pylint: disable=W0614,W0401

DEBUG = False

UMAP_ALLOW_ANONYMOUS = True
SITE_URL = "https://dev.umap-project.org"
ADMINS = getaddresses([env("DJANGO_ADMINS")])
MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "umap",
    }
}

LANGUAGE_CODE = "en"

WSGI_APPLICATION = "umap.wsgi.application"

AUTHENTICATION_BACKENDS = (
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.twitter_oauth2.TwitterOAuth2",
    "social_core.backends.openstreetmap_oauth2.OpenStreetMapOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)
SOCIAL_AUTH_GITHUB_KEY = env("SOCIAL_AUTH_GITHUB_KEY", default="")
SOCIAL_AUTH_GITHUB_SECRET = env("SOCIAL_AUTH_GITHUB_SECRET", default="")
# We need email to associate with other Oauth providers
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]
SOCIAL_AUTH_TWITTER_OAUTH2_KEY = env("SOCIAL_AUTH_TWITTER_OAUTH2_KEY", default="")
SOCIAL_AUTH_TWITTER_OAUTH2_SECRET = env("SOCIAL_AUTH_TWITTER_OAUTH2_SECRET", default="")
MIDDLEWARE += ("social_django.middleware.SocialAuthExceptionMiddleware",)
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_BACKEND_ERROR_URL = "/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/"

UMAP_DEMO_PK = 204
# UMAP_SHOWCASE_PK = 1373
UMAP_DEMO_SITE = True
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/srv/umap/cache",
    }
}
UMAP_USE_UNACCENT = True
STATIC_ROOT = "/srv/umap/static_root"
MEDIA_ROOT = "/srv/umap/media_root"
UMAP_XSENDFILE_HEADER = "X-Accel-Redirect"
ALLOWED_HOSTS = [
    "dev.umap-project.org",
    "dev.umap-project.org.",
]
UMAP_EXCLUDE_DEFAULT_MAPS = True
UMAP_KEEP_VERSIONS = 5
UMAP_GZIP = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "ERROR",
            "filters": None,
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
    },
}

DEFAULT_FROM_EMAIL = env("FROM_EMAIL", default="")
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = 587
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

UMAP_CUSTOM_TEMPLATES = "/srv/umap/theme/templates"
DEPRECATED_AUTHENTICATION_BACKENDS = [
    "social_core.backends.twitter_oauth2.TwitterOAuth2"
]

UMAP_IMPORTERS = {
    "opendata": {},
    "geodatamine": {},
    "overpass": {"url": "https://overpass-api.de/api/interpreter"},
    "communesfr": {},
    "banfr": {},
    "datasets": {
        "choices": [
            {
                "label": "Régions",
                "url": "https://france-geojson.gregoiredavid.fr/repo/regions.geojson",
                "format": "geojson",
            },
            {
                "label": "Départements",
                "url": "https://france-geojson.gregoiredavid.fr/repo/departements.geojson",
                "format": "geojson",
            },
            {
                "label": "Arrondissements de Paris",
                "url": "https://geo.api.gouv.fr/communes?codeParent=75056&type=arrondissement-municipal&format=geojson&geometry=contour",
                "format": "geojson",
            },
            {
                "label": "Arrondissements de Marseille",
                "url": "https://geo.api.gouv.fr/communes?codeParent=13055&type=arrondissement-municipal&format=geojson&geometry=contour",
                "format": "geojson",
            },
            {
                "label": "Arrondissements de Lyon",
                "url": "https://geo.api.gouv.fr/communes?codeParent=69123&type=arrondissement-municipal&format=geojson&geometry=contour",
                "format": "geojson",
            },
        ]
    },
}

UMAP_HOST_INFOS = {
    "name": "Enix",
    "url": "https://enix.io/fr/legal/",
    "email": "contact@umap-project.org",
}
UMAP_LABEL_KEYS = ["name", "title", "nom"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
REALTIME_ENABLED = True

import sentry_sdk

sentry_sdk.init(
    dsn=env("SENTRY_DNS", default=""),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=0.1,
    environment=env("SENTRY_ENVIRONMENT", default="dev"),
)
