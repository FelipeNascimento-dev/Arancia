import os

from setup.environments import apply_environment

SECRET_KEY = ']s5n/RoBy<&r;f91C2C|1F"{SDJ!dr!("[)DvU#jzC6Gu.y">LozaG"{>A.te'
ENVIRONMENT = 'prod'
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

# Integração CRM (FastAPI) — secret por ambiente via apply_environment; env sobrescreve
CRM_API_V1_STR = '/api/v1'
CRM_API_TIMEOUT = 30
CRM_API_VERIFY_SSL = False
CRM_DEFAULT_LIMIT = 100
CRM_SERVICE_USER_ID = 1
CRM_SERVICE_USERNAME = 'celery'

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
