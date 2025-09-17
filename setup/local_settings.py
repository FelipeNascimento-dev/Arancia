SECRET_KEY = ']s5n/RoBy<&r;f91C2C|1F"{SDJ!dr!("[)DvU#jzC6Gu.y">LozaG"{>A.te'
LOCAL_DEBUG = False
if LOCAL_DEBUG:
    API_KEY_INTELIPOST = '2c7b1f95-9dfc-2e5e-d844-ece50622eb54eacv'
    API_URL = 'http://192.168.0.216/homo-fulfillment'
    DB_HOST = '192.168.0.219'
else:
    API_KEY_INTELIPOST = 'e92231bc-18a9-033b-738d-2039f9452e12etyu'
    DB_HOST = '192.168.0.220'
    API_URL = 'http://192.168.0.216/fulfillment'

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
    'www.centralretencao.com.br'
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





#CONTROLE DE CAMPO
from datetime import date
API_BASE = "http://127.0.0.1:8000/RetencaoAPI"
COD_BASE = "CTBSEQ"
COD_EMPRESA = "CLARO"
TOKEN = "123"

API_TECNICOS = f"{API_BASE}/api/v3/tecnicos/buscar_tec"
API_RESUMO = f"{API_BASE}/api/v3/Filtro_status/resumo-status-detalhado/{COD_EMPRESA}?date={date.today()}"
API_HORARIO = f"{API_BASE}/api/v3/dashboard/ocorrencias-por-horario/{COD_EMPRESA}?date={date.today()}"

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

