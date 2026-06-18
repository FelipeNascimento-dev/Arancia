from pathlib import Path

from celery.schedules import crontab

from setup import local_settings
from setup.cache_settings import build_caches, build_redis_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wg8bt!49d#axro8-8299a1pup&&f*kueeu=%x=2)k0i(0@rtpj'

# SECURITY WARNING: don't run with debug turned on in production!
# Legado: DEBUG=True é exigido por partes do projeto; não alterar sem auditoria.
# Sobrescreva em local_settings.py apenas após validar dependências.
DEBUG = getattr(local_settings, 'DEBUG', True)

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "logistica.apps.LogisticaConfig",
    'transportes', 'backoffice',
    'mural',
    'crm.apps.CrmConfig',
    'projetos.apps.ProjetosConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'setup.middleware.auto_logout.AutoLogoutMiddleware',
    "setup.middleware.crm_http_client.CrmHttpClientMiddleware",
    "setup.middleware.password_expiration.PasswordExpirationMiddleware",
    "setup.middleware.request_timing.RequestTimingMiddleware",
]

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'base_templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'setup.settings.environment_context',
                'logistica.context_processors.avatar_url',
                'logistica.context_processors.acompanhamentos_navbar',
                'crm.context_processors.crm_menu_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'setup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'base_static',
]
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de autenticação Django
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'


_REDIS_ENABLED = getattr(local_settings, 'REDIS_ENABLED', True)
_REDIS_HOST = getattr(local_settings, 'REDIS_HOST', '127.0.0.1')
_REDIS_PORT = int(getattr(local_settings, 'REDIS_PORT', 6379))
_REDIS_PASSWORD = getattr(local_settings, 'REDIS_PASSWORD', '')
_REDIS_CELERY_DB = int(getattr(local_settings, 'REDIS_CELERY_DB', 0))
_CELERY_REDIS_URL = build_redis_url(
    host=_REDIS_HOST,
    port=_REDIS_PORT,
    db=_REDIS_CELERY_DB,
    password=_REDIS_PASSWORD,
)

CELERY_BROKER_URL = getattr(local_settings, 'CELERY_BROKER_URL', _CELERY_REDIS_URL)
CELERY_RESULT_BACKEND = getattr(local_settings, 'CELERY_RESULT_BACKEND', _CELERY_REDIS_URL)


# Configuração de agendamento
CELERY_BEAT_SCHEDULE = {
    "desativar-usuarios-inativos-todos-os-dias": {
        "task": "logistica.tasks.deactivate_inactive_users",
        "schedule": crontab(hour=3, minute=0),
    },
    "crm-gerar-tasks-recorrentes": {
        "task": "crm.tasks.generate_recurring_tasks",
        "schedule": crontab(minute="*/15"),
    },
    "crm-disparar-alertas-contrato": {
        "task": "crm.tasks.fire_contract_alerts",
        "schedule": crontab(hour=8, minute=0),
    },
}

try:
    from setup.local_settings import *
except ImportError:
    ...

CRM_API_BASE_URL = getattr(local_settings, 'CRM_API_BASE_URL', '')
CRM_API_V1_STR = getattr(local_settings, 'CRM_API_V1_STR', '/api/v1')
CRM_API_KEY = getattr(local_settings, 'CRM_API_KEY', '')
CRM_INTERNAL_API_SECRET = getattr(local_settings, 'CRM_INTERNAL_API_SECRET', '')
CRM_API_TIMEOUT = int(getattr(local_settings, 'CRM_API_TIMEOUT', 30))
CRM_API_VERIFY_SSL = getattr(local_settings, 'CRM_API_VERIFY_SSL', False)
CRM_SERVICE_USERNAME = getattr(local_settings, 'CRM_SERVICE_USERNAME', '')
CRM_SERVICE_PASSWORD = getattr(local_settings, 'CRM_SERVICE_PASSWORD', '')
CRM_COMERCIAL_BOARD_CODE = getattr(local_settings, 'CRM_COMERCIAL_BOARD_CODE', 'crm_comercial')
ENVIRONMENT = getattr(local_settings, 'ENVIRONMENT', 'homolog')

# Instrumentação de performance (Fase 0) — ativar em dev/homolog via local_settings
PERFORMANCE_INSTRUMENTATION = getattr(local_settings, 'PERFORMANCE_INSTRUMENTATION', False)
CRM_MENU_CONTEXT_CACHE_TTL = int(getattr(local_settings, 'CRM_MENU_CONTEXT_CACHE_TTL', 90))
CRM_LOOKUPS_REDIS_CACHE_TTL = int(getattr(local_settings, 'CRM_LOOKUPS_REDIS_CACHE_TTL', 300))
CRM_ME_CONTEXT_REDIS_CACHE_TTL = int(
    getattr(local_settings, 'CRM_ME_CONTEXT_REDIS_CACHE_TTL', 300)
)
CRM_REDIS_CACHE_ENABLED = getattr(local_settings, 'CRM_REDIS_CACHE_ENABLED', _REDIS_ENABLED)
ACOMPANHAMENTOS_NAVBAR_CACHE_TTL = int(
    getattr(local_settings, 'ACOMPANHAMENTOS_NAVBAR_CACHE_TTL', 600)
)

# Cache Django — Redis (Fase 3); LocMem quando REDIS_ENABLED=false
CACHES = build_caches(
    redis_enabled=_REDIS_ENABLED,
    redis_host=_REDIS_HOST,
    redis_port=_REDIS_PORT,
    redis_db=int(getattr(local_settings, 'REDIS_DB', 1)),
    redis_password=_REDIS_PASSWORD,
    redis_max_connections=int(getattr(local_settings, 'REDIS_MAX_CONNECTIONS', 50)),
    redis_socket_timeout=float(getattr(local_settings, 'REDIS_SOCKET_TIMEOUT', 2.0)),
    redis_socket_connect_timeout=float(
        getattr(local_settings, 'REDIS_SOCKET_CONNECT_TIMEOUT', 2.0)
    ),
)

_IS_HOMOLOG_ENV = getattr(local_settings, 'ENVIRONMENT', 'homolog') == 'homolog'
_CRM_API_LOG_LEVEL = 'DEBUG' if (
    _IS_HOMOLOG_ENV or PERFORMANCE_INSTRUMENTATION
) else 'WARNING'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'crm_api': {
            'handlers': ['console'],
            'level': _CRM_API_LOG_LEVEL,
            'propagate': False,
        },
    },
}

def environment_context(request):
    """Expõe ambiente atual (homolog/prod) para templates."""
    environment = getattr(local_settings, 'ENVIRONMENT', None)
    if environment is None:
        environment = 'homolog' if getattr(local_settings, 'LOCAL_DEBUG', False) else 'prod'
    return {
        'DB_HOST': getattr(local_settings, 'DB_HOST', None),
        'ENVIRONMENT': environment,
        'IS_HOMOLOG': environment == 'homolog',
        'BASE_PATH': getattr(local_settings, 'BASE_PATH', ''),
    }


# Alias legado — manter até remover referências antigas
db_host_context = environment_context


# RESET DE SENHAS / ENVIO POR EMAIL

EMAIL_SMTP_HOST = "email-ssl.com.br"
EMAIL_SMTP_PORT = 465
EMAIL_USER = "system@c-trends.com.br"
EMAIL_PASS = "@System#CTB2026"

PASSWORD_EXPIRATION_DAYS = 30
PASSWORD_WARNING_DAYS = 7
PASSWORD_RESET_CODE_EXPIRATION_MINUTES = 15
