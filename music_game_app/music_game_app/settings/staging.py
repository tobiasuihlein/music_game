from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours

STATIC_ROOT = '/app/staticfiles'
STATIC_URL = 'static/'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'