import os

SECRET_KEY = ']s5n/RoBy<&r;f91C2C|1F"{SDJ!dr!("[)DvU#jzC6Gu.y">LozaG"{>A.te'
LOCAL_DEBUG = False
if LOCAL_DEBUG:
    API_KEY_INTELIPOST = '2c7b1f95-9dfc-2e5e-d844-ece50622eb54eacv'
    API_URL = 'http://192.168.0.216/homo-fulfillment'
    STOCK_API_URL = 'http://192.168.0.214/hg-stock/api'
    TRANSP_API_URL = 'http://192.168.0.215/hg-api-transportes/api'
    MURAL_API_URL = 'http://192.168.0.214/hg-api-mural/api'
    # Homolog — alinhado ao padrão hg-api-* (.214); local: http://localhost:8000
    CRM_API_BASE_URL = os.environ.get(
        'CRM_API_BASE_URL', 'http://192.168.0.214/hg-api-crm'
    )
    CRM_INTERNAL_API_SECRET = os.environ.get(
        'CRM_INTERNAL_API_SECRET', 'homolog-internal-secret'
    )
    DB_HOST = '192.168.0.220'
else:
    API_KEY_INTELIPOST = 'e92231bc-18a9-033b-738d-2039f9452e12etyu'
    DB_HOST = '192.168.0.220'
    API_URL = 'http://192.168.0.214/fulfillment'
    STOCK_API_URL = 'http://192.168.0.214/stock/api'
    TRANSP_API_URL = 'http://192.168.0.216/api-transportes/api'
    MURAL_API_URL = 'http://192.168.0.215/api-mural/api'
    # Produção — alinhado ao padrão api-* (.215)
    CRM_API_BASE_URL = os.environ.get(
        'CRM_API_BASE_URL', 'http://192.168.0.215/api-crm'
    )
    CRM_INTERNAL_API_SECRET = os.environ.get(
        'CRM_INTERNAL_API_SECRET', 'd5u7sA8x0bB3Q0fAw@$'
    )

# Integração CRM (FastAPI) — secret por ambiente acima; env sobrescreve
CRM_API_V1_STR = '/api/v1'
CRM_API_TIMEOUT = 30
CRM_API_VERIFY_SSL = False  # HTTP interno sem TLS (mesmo padrão das demais APIs)
CRM_DEFAULT_LIMIT = 100
CRM_SERVICE_USER_ID = 1
CRM_SERVICE_USERNAME = 'celery'


URL_LABEL_INTELIPOST = 'https://api.intelipost.com.br/api/v1/shipment_order/get_label/'


PROJECT_BASE_PATH = '/arancia/'

STATIC_URL = '/arancia/static/'
LOGIN_REDIRECT_URL = '/arancia/'

ALLOWED_HOSTS: list[str] = [
    'localhost',
    '127.0.0.1',
    '192.168.0.214',
    '192.168.0.215',
    '192.168.0.216',
    'https://www.centralretencao.com.br',
    'www.centralretencao.com.br',
    'http://kuma.wolf.local',
    'kuma.wolf.local'
]
CSRF_TRUSTED_ORIGINS: list[str] = [
    'http://localhost',
    'http://127.0.0.1',
    'http://192.168.0.214',
    'http://192.168.0.215',
    'http://192.168.0.216',
    'https://www.centralretencao.com.br',
    'http://www.centralretencao.com.br'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'arancia_db',
        'USER': 'sa',
        'PASSWORD': 'Profeta_01',
        'HOST': DB_HOST,  # ou o IP do servidor
        'PORT': '5432',       # padrão do PostgreSQL
    }
}


# CONTROLE DE CAMPO

API_BASE = "http://192.168.0.216/RetencaoAPI/api"
TOKEN = "K90nIR4PK90nIR4PBKIy0rPZ6uwSqKCDX"
API_BASE_BKO = "http://192.168.0.214/api-equipamentos/api/"
# Mapas
status_labels = {
    "concluido": "Concluído",
    "no_tempo": "No Tempo",
    "no_limite": "No Limite",
    "atrasado": "Atrasado",
    "sem_horario_definido": "Sem Horário",
}
status_colors = {
    "concluido": "bg-blue-600",
    "no_tempo": "bg-green-600",
    "no_limite": "bg-yellow-500",
    "atrasado": "bg-red-600",
    "sem_horario_definido": "bg-gray-500"
}
