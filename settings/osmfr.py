from email.utils import getaddresses

from umap.settings.base import *  # pylint: disable=W0614,W0401

DEBUG = False
# TEMPLATE_DEBUG = DEBUG
STATIC_ROOT = "/srv/umap/static_root"
MEDIA_ROOT = "/srv/umap/media_root"
#
ADMINS = getaddresses([env("DJANGO_ADMINS")])
MANAGERS = ADMINS
ALLOWED_HOSTS = ["umap.openstreetmap.fr", "127.0.0.1", "dev.umap.openstreetmap.fr"]
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "umap",
        "PORT": 5432,
    }
}
CONN_MAX_AGE = 60

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/srv/umap/cache",
    }
}

WSGI_APPLICATION = "umap.wsgi.application"

AUTHENTICATION_BACKENDS = (
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.bitbucket.BitbucketOAuth",
    "social_core.backends.twitter_oauth2.TwitterOAuth2",
    "social_core.backends.openstreetmap_oauth2.OpenStreetMapOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)
SOCIAL_AUTH_GITHUB_KEY = env("SOCIAL_AUTH_GITHUB_KEY", default="")
SOCIAL_AUTH_GITHUB_SECRET = env("SOCIAL_AUTH_GITHUB_SECRET", default="")
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]
SOCIAL_AUTH_TWITTER_KEY = env("SOCIAL_AUTH_TWITTER_KEY", default="")
SOCIAL_AUTH_TWITTER_SECRET = env("SOCIAL_AUTH_TWITTER_SECRET", default="")
SOCIAL_AUTH_BITBUCKET_KEY = env("SOCIAL_AUTH_BITBUCKET_KEY", default="")
SOCIAL_AUTH_BITBUCKET_SECRET = env("SOCIAL_AUTH_BITBUCKET_SECRET", default="")
MIDDLEWARE += ("social_django.middleware.SocialAuthExceptionMiddleware",)
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_BACKEND_ERROR_URL = "/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/"

UMAP_DEMO_PK = 1
# UMAP_SHOWCASE_PK = 4783
# UMAP_DEMO_SITE = True
SITE_URL = "https://umap.openstreetmap.fr"
SHORT_SITE_URL = "http://u.osmfr.org"

LANGUAGE_CODE = "en"

UMAP_ALLOW_ANONYMOUS = True

UMAP_USE_UNACCENT = True

UMAP_EXCLUDE_DEFAULT_MAPS = True

UMAP_XSENDFILE_HEADER = "X-Accel-Redirect"

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

UMAP_MAPS_PER_SEARCH = 10
UMAP_SEARCH_CONFIGURATION = "umapdict"
UMAP_MAPS_PER_PAGE_OWNER = 30

UMAP_CUSTOM_TEMPLATES = "/srv/umap/theme/templates"

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
    environment="osmfr",
)
