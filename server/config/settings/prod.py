import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

from .base import *

DEBUG = True
ALLOWED_HOSTS=['10.85.198.140', 'localhost', '127.0.0.1']
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME':     os.environ['DB_NAME'],
#         'USER':     os.environ['DB_USER'],
#         'PASSWORD': os.environ['DB_PASSWORD'],
#         'HOST':     os.environ.get('DB_HOST', 'localhost'),
#         'PORT':     os.environ.get('DB_PORT', '5432'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_ORIGIN')
EMAIL_HOST_PASSWORD = os.environ.get('GOOGLE_APP_PASSWORD') 
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
FRONTEND_URL = 'http://127.0.0.1:8000'