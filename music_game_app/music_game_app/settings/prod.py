from .base import *

DEBUG = True
ALLOWED_HOSTS = [
    'tobiasuihlein.de',
    'www.tobiasuihlein.de',
    '138.201.135.222', # server IP
    '10.0.10.210', # VM IP
    'localhost',
    '127.0.0.1'
]

# Trust X-Forwarted-Proto header from reverse proxy after SSL termination
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours

STATIC_ROOT = '/app/staticfiles'
STATIC_URL = 'static/'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'