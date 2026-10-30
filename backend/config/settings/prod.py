from .base import *
import environ
from django.core.exceptions import ImproperlyConfigured

env = environ.Env()
SECRET_KEY = env('DJANGO_SECRET_KEY')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure'):
    raise ImproperlyConfigured('Configure uma chave secreta forte de pelo menos 50 caracteres.')
DEBUG = False
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
DATABASES = {'default': env.db('DATABASE_URL')}
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
AUTH_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
if env.bool('TRUST_PROXY_SSL_HEADER', default=False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
STATIC_ROOT = BASE_DIR / 'staticfiles'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
FRONTEND_URL = env('FRONTEND_URL')
