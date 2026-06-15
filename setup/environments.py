"""
Perfis de ambiente Arancia (homolog / prod).

URLs, hosts e paths versionáveis. Secrets (TOKEN, API keys) ficam em
local_settings.py ou variáveis de ambiente — não neste módulo.
"""
import os

VALID_ENVIRONMENTS = ('homolog', 'prod')

ENVIRONMENT_PROFILES = {
    'homolog': {
        'label': 'Homologação',
        'db_host': '192.168.0.219',
        'base_path': 'hg-arancia/',
        'api_url': 'http://192.168.0.216/homo-fulfillment',
        'stock_api_url': 'http://192.168.0.214/hg-stock/api',
        'transp_api_url': 'http://192.168.0.215/hg-api-transportes/api',
        'mural_api_url': 'http://192.168.0.214/hg-api-mural/api',
        # TODO: validar URL homolog RetencaoAPI com TI antes de deploy
        'api_base': 'http://192.168.0.214/hg-RetencaoAPI/api',
        'api_base_bko': 'http://192.168.0.214/hg-api-equipamentos/api/',
        'crm_api_base_url_default': 'http://192.168.0.214/hg-api-crm',
        'crm_internal_api_secret_default': 'homolog-internal-secret',
    },
    'prod': {
        'label': 'Produção',
        'db_host': '192.168.0.220',
        'base_path': 'arancia/',
        'api_url': 'http://192.168.0.216/fulfillment',
        'stock_api_url': 'http://192.168.0.214/stock/api',
        'transp_api_url': 'http://192.168.0.216/api-transportes/api',
        'mural_api_url': 'http://192.168.0.215/api-mural/api',
        'api_base': 'http://192.168.0.216/RetencaoAPI/api',
        'api_base_bko': 'http://192.168.0.214/api-equipamentos/api/',
        'crm_api_base_url_default': 'http://192.168.0.215/api-crm',
        'crm_internal_api_secret_default': 'd5u7sA8x0bB3Q0fAw@$',
    },
}


def normalize_environment(environment):
    """Valida e normaliza o nome do ambiente."""
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"Ambiente inválido: {environment!r}. "
            f"Use um de: {', '.join(VALID_ENVIRONMENTS)}"
        )
    return environment


def get_profile(environment):
    """Retorna o dicionário de perfil para o ambiente informado."""
    return ENVIRONMENT_PROFILES[normalize_environment(environment)]


def apply_environment(environment, namespace):
    """
    Aplica variáveis do perfil no namespace do módulo (ex.: globals() de local_settings).

    CRM_API_BASE_URL e CRM_INTERNAL_API_SECRET aceitam override via env var.
    """
    env = normalize_environment(environment)
    profile = get_profile(env)

    namespace['ENVIRONMENT'] = env
    namespace['LOCAL_DEBUG'] = env == 'homolog'

    namespace['DB_HOST'] = profile['db_host']
    namespace['BASE_PATH'] = profile['base_path']
    namespace['PROJECT_BASE_PATH'] = f"/{profile['base_path']}"
    namespace['STATIC_URL'] = f"/{profile['base_path']}static/"
    namespace['LOGIN_REDIRECT_URL'] = f"/{profile['base_path']}"

    namespace['API_URL'] = profile['api_url']
    namespace['STOCK_API_URL'] = profile['stock_api_url']
    namespace['TRANSP_API_URL'] = profile['transp_api_url']
    namespace['MURAL_API_URL'] = profile['mural_api_url']
    namespace['API_BASE'] = profile['api_base']
    namespace['API_BASE_BKO'] = profile['api_base_bko']

    namespace['CRM_API_BASE_URL'] = os.environ.get(
        'CRM_API_BASE_URL', profile['crm_api_base_url_default']
    )
    namespace['CRM_INTERNAL_API_SECRET'] = os.environ.get(
        'CRM_INTERNAL_API_SECRET', profile['crm_internal_api_secret_default']
    )

    if 'DATABASES' in namespace and isinstance(namespace['DATABASES'], dict):
        default_db = namespace['DATABASES'].get('default')
        if isinstance(default_db, dict):
            default_db['HOST'] = profile['db_host']
