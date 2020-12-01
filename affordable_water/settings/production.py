import os

# pylint:disable=unused-wildcard-import
from affordable_water.settings.base import * # noqa: F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False
DEBUG_PROPAGRATE_EXCEPTIONS = False

ALLOWED_HOSTS = [
    os.getenv('HOSTNAME'),
    'getwaterwisebuffalo.org'
]

ADMINS = [
    (os.getenv('ADMIN_NAME'), os.getenv('ADMIN_EMAIL')),
]

SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': False
        },
    },
]