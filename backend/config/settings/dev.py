from .base import *
import os

DEBUG = True
# IPs extras da LAN (ex.: acesso pelo celular): FLUIDMES_LAN_IP=192.168.0.10,192.168.0.11
LAN_IPS = [ip.strip() for ip in os.environ.get('FLUIDMES_LAN_IP', '').split(',') if ip.strip()]
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver', *LAN_IPS]
LAN_ORIGINS = [f'http://{address}:5173' for address in LAN_IPS]
CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, *LAN_ORIGINS]
CORS_ALLOWED_ORIGINS = [*CORS_ALLOWED_ORIGINS, *LAN_ORIGINS]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@fluidmes.com'
FRONTEND_URL = os.environ.get('FRONTEND_URL', f'http://{LAN_IPS[0] if LAN_IPS else "localhost"}:5173')
if os.environ.get('DATABASE_URL'):
    import environ
    DATABASES = {'default': environ.Env().db_url('DATABASE_URL')}

# Basic local UI/simulation does not require Redis. For cross-process telemetry,
# set REDIS_URL on both the API and read_plants processes.
if not os.environ.get('REDIS_URL'):
    CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
