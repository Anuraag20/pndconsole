"""
Django settings for pndconsole project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import configparser
import json
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

config = configparser.ConfigParser()
config.read(BASE_DIR / 'pndconsole/config.ini')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['django-settings']['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config['django-settings']['DEBUG']

ALLOWED_HOSTS = json.loads( config['django-settings']['ALLOWED_HOSTS'] )
 


# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'rest_framework',
    'django_celery_beat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pnds',
    'market',
    'forums',
    'llm',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pndconsole.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pndconsole.wsgi.application'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CSRF_TRUSTED_ORIGINS = json.loads( config['django-settings']['CSRF_TRUSTED_ORIGINS'] )

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOGIN_URL = '/admin/login/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static/'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


GEMINI_API_KEY = config['gemini-flash']['API_KEY']
COIN_PROMPT_PATH = BASE_DIR / 'llm/prompts/coin-prompt.txt'
SCHEDULE_PROMPT_PATH = BASE_DIR / 'llm/prompts/prompt-test.txt'


CELERY_BROKER_URL = config['django-settings']['CELERY_BROKER_URL']
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

ASGI_APPLICATION = "pndconsole.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{ "address": config['django-settings']['REDIS_URL'] }],
        },
    },
}

WEB_SOCKET_BASE_URL = config['django-settings']['WEB_SOCKET_BASE_URL'] 
FINE_GRAINED_MONITORING_BEFORE = timedelta(minutes = 15)

STOP_PRODUCING_AFTER = timedelta(minutes = 30)
STOP_CONSUMING_AFTER = STOP_PRODUCING_AFTER
# This variable is useful when consumption and production are done by separate processes
FETCH_PREVIOUS_DEFAULT = timedelta(hours = 1)

# Variable controlling after how many messages the data for the current minute is resent to the consumer
RESEND_CURRENT_MIN_AFTER = 5
CELERY_STREAMING_VERSION = 2
STREAMING_VERSION = 2

