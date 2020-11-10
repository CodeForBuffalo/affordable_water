# pylint:disable=unused-wildcard-import
from affordable_water.settings.base import * # noqa: F401

SECRET_KEY = 'thisSecretKeyIsOnlyUsedDuringLocalDevelopment' # noqa: secret

DEBUG = True
DEBUG_PROPAGRATE_EXCEPTIONS = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'testserver'
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
            'debug': True
        },
    },
]