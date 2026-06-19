import os

from setup.environments import apply_environment

SECRET_KEY = ']s5n/RoBy<&r;f91C2C|1F"{SDJ!dr!("[)DvU#jzC6Gu.y">LozaG"{>A.te'
ENVIRONMENT = 'homolog'
# Secrets por ambiente (permanecem neste arquivo, não em environments.py)
_ENVIRONMENT_SECRETS = {
    'homolog': {
        'API_KEY_INTELIPOST': '2c7b1f95-9dfc-2e5e-d844-ece50622eb54eacv',
        'TOKEN': 'K90nIR4PK90nIR4PBKIy0rPZ6uwSqKCDX',
    },
    'prod': {
        'API_KEY_INTELIPOST': 'e92231bc-18a9-033b-738d-2039f9452e12etyu',
        'TOKEN': 'K90nIR4PK90nIR4PBKIy0rPZ6uwSqKCDX',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'arancia_db',
        'USER': 'sa',
        'PASSWORD': 'Profeta_01',
        'HOST': '192.168.0.219',
        'PORT': '5432',
    }
}

apply_environment(ENVIRONMENT, globals())

# Alias legado — LOCAL_DEBUG significa "ambiente homolog"
LOCAL_DEBUG = ENVIRONMENT == 'homolog'

for _key, _value in _ENVIRONMENT_SECRETS[ENVIRONMENT].items():
    globals()[_key] = _value

URL_LABEL_INTELIPOST = 'https://api.intelipost.com.br/api/v1/shipment_order/get_label/'

ALLOWED_HOSTS: list[str] = [
    'localhost',
    '127.0.0.1',
    '192.168.0.214',
    '192.168.0.215',
    '192.168.0.216',
    'https://www.centralretencao.com.br',
    'www.centralretencao.com.br',
    'http://kuma.wolf.local',
    'kuma.wolf.local',
]
CSRF_TRUSTED_ORIGINS: list[str] = [
    'http://localhost',
    'http://127.0.0.1',
    'http://192.168.0.214',
    'http://192.168.0.215',
    'http://192.168.0.216',
    'https://www.centralretencao.com.br',
    'http://www.centralretencao.com.br',
]

# Mapas — controle de campo (independente de ambiente)
status_labels = {
    'concluido': 'Concluído',
    'no_tempo': 'No Tempo',
    'no_limite': 'No Limite',
    'atrasado': 'Atrasado',
    'sem_horario_definido': 'Sem Horário',
}
status_colors = {
    'concluido': 'bg-blue-600',
    'no_tempo': 'bg-green-600',
    'no_limite': 'bg-yellow-500',
    'atrasado': 'bg-red-600',
    'sem_horario_definido': 'bg-gray-500',
}

# Redis — mesmo host da API CRM FastAPI; Django cache usa db 1, Celery db 0
REDIS_ENABLED = False
REDIS_HOST = '192.168.0.221'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_PASSWORD = ''
REDIS_MAX_CONNECTIONS = 50
REDIS_SOCKET_TIMEOUT = 2.0
REDIS_SOCKET_CONNECT_TIMEOUT = 2.0
REDIS_CELERY_DB = 0

# CRM API — Basic Auth (usuário logado) + X-API-Key
CRM_API_KEY = 'F7UuScgkRNn2rrSFWM0yuqkbI9RlOuuwPYyC1RPVe8KW'

CRM_INTERNAL_API_SECRET = 'homolog-internal-secret'

# Usuário operacional para jobs Celery (X-Acting-User em modo Bearer)
CRM_SERVICE_USERNAME = os.environ.get('CRM_SERVICE_USERNAME', 'celery')