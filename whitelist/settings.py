"""
Django settings for whitelist project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime
from urllib import parse

import sentry_sdk
import dj_database_url

from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '8#rqlz945qoz642e!-a2cu4j&1u(=afblh_x$$&fiww319ue8*')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'mojang',
    'twitch',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitelist.middleware.LogExceptions',
]

# Additional tools for DEBUG mode
if DEBUG:
    INSTALLED_APPS.append('django_extensions')
    MIDDLEWARE += (
        'whitelist.middleware.LogRequestData',
        'whitelist.middleware.TimeRequests',
    )

# Otherwise set up logging with Sentry
else:
    sentry_sdk.init(
        dsn='https://51a878d10dbb4ddfb83843a613f3b23b@sentry.wearelucida.com/3',
        send_default_pii=True,
        integrations=[DjangoIntegration()]
    )


ROOT_URLCONF = 'whitelist.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'whitelist.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default='postgres://postgres:postgres@postgis/whitelist', conn_max_age=600),
}


# Caches
DUMMY_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
}

redis_url = parse.urlparse(os.environ.get('REDIS_URL', 'redis://redis:6379'))
REDIS_CACHE = {
    'default': {
         'BACKEND': 'redis_cache.RedisCache',
         'LOCATION': '{0}:{1}'.format(redis_url.hostname, redis_url.port),
         'TIMEOUT': None,
         'OPTIONS': {
             'PASSWORD': redis_url.password,
             'DB': 0,
         }
    }
}
CACHES = REDIS_CACHE if os.environ.get('NO_CACHE', 'False') != 'True' else DUMMY_CACHE


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)


# Social Auth
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

AUTHENTICATION_BACKENDS = (
    'social_core.backends.twitch.TwitchOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Twitch Configuration
SOCIAL_AUTH_TWITCH_KEY = os.environ.get('TWITCH_KEY', '')
SOCIAL_AUTH_TWITCH_SECRET = os.environ.get('TWITCH_SECRET', '')
SOCIAL_AUTH_TWITCH_SCOPE = [
    # v5 (unitl New API has the functionality)
    'user_subscriptions',
    # New API
    'channel:read:subscriptions',
]

SOCIAL_AUTH_TWITCH_EXTRA_DATA = [
    ('access_token', 'access_token'),
    ('refresh_token', 'refresh_token'),
    ('expires_in', 'expires'),
    ('token_type', 'token_type')
]

SOCIAL_AUTH_TWITCH_BROADCASTER_SCOPE = [

]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/profile'

# Update our logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        }
    },
}

try:
    from .local_settings import *
except ImportError:
    pass
