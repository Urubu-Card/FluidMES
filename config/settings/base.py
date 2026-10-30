from pathlib import Path
import os
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'development-only-not-for-production-fluidmes')

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.plantas',
    'apps.producao',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#CORS_ALLOW_ALL_ORIGINS = True #Nao utilizar em prod XD
CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'pages'],   #* Templates na raiz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'accounts.Usuarios'

AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.MultiLogin',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'anon': '60/hour', 'auth': '10/minute'},
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.accounts.authentication.JWTCookieAuthentication',
    ),
}


ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")],#? Utilização do redis com docker
        },
    },
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

#* Configurações do tempo do token
SIMPLE_JWT = {
    'CHECK_REVOKE_TOKEN': True,
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'UPDATE_LAST_LOGIN': True,

}

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/1')#? O "/1" especifica o namespace
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TIMEZONE = TIME_ZONE

STATIC_URL = '/static/'
#STATICFILES_DIRS = [BASE_DIR / 'static']

LOGIN_URL = 'login'

AUTH_COOKIE_ACCESS = 'access_token'
AUTH_COOKIE_REFRESH = 'refresh_token'
AUTH_COOKIE_HTTPONLY = True
AUTH_COOKIE_SAMESITE = 'Lax'
AUTH_COOKIE_SECURE = False   #! True em PROD
CSRF_COOKIE_SECURE = False
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:8080', 'http://127.0.0.1:8080']
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {'daily-oee': {'task': 'apps.producao.tasks.calcular_oee_diario', 'schedule': crontab(hour=1, minute=0)}}

SIMULACAO_PRODUCAO = os.environ.get('SIMULACAO_PRODUCAO', 'true').lower() == 'true'

# Execução real por Modbus (plantas cujo CLP tem um tanque TK1/TK2 definido).
# Escalas: unidades do registro por litro e por segundo.
MODBUS_ESCALA_NIVEL = float(os.environ.get('MODBUS_ESCALA_NIVEL', '1'))
MODBUS_ESCALA_TEMPO = float(os.environ.get('MODBUS_ESCALA_TEMPO', '1'))
# Segundos de espera pelo STATUS "em ciclo" após o START_CYCLE antes de repetir.
# Valor do registro STATUS que significa "tanque em ciclo".
MODBUS_STATUS_EM_CICLO = int(os.environ.get('MODBUS_STATUS_EM_CICLO', '1'))
MODBUS_TIMEOUT_PARTIDA_SEG = float(os.environ.get('MODBUS_TIMEOUT_PARTIDA_SEG', '15'))
