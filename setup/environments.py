"""
Perfis de ambiente Arancia (homolog / prod).

URLs, hosts e paths versionáveis. Secrets (TOKEN, API keys) ficam em
local_settings.py ou variáveis de ambiente — não neste módulo.
"""

VALID_ENVIRONMENTS = ('homolog', 'prod')

# IDs de GET {stock_api_url}/v1/origins
_ORDER_ORIGIN_IDS_HOMOLOG = {
    'SAP_CACA_POS_AGUARDANDO_REVERSA': 1,
    'LAST_MILE_SUPRIMENTO': 3,
    'REVERSA_AGUARDANDO': 8,
    'LAST_MILE_AGUARDANDO_REVERSA': 9,
    'SAP_CACA_POS_AGUARDANDO_REVERSA_PROVISORIO': 10,
    'REVERSA_AGUARDANDO_PROVISORIO': 11,
    'LAST_MILE_AGUARDANDO_REVERSA_PROVISORIO': 12,
    'SAP_BAU_SUPRIMENTO': 13,
}

_ORDER_ORIGIN_IDS_PROD = {
    'SAP_CACA_POS_AGUARDANDO_REVERSA': 1,
    'LAST_MILE_SUPRIMENTO': 3,
    'LAST_MILE_AGUARDANDO_REVERSA': 9,
    'REVERSA_AGUARDANDO': 10,
    'SAP_CACA_POS_AGUARDANDO_REVERSA_PROVISORIO': 11,
    'REVERSA_AGUARDANDO_PROVISORIO': 12,
    'LAST_MILE_AGUARDANDO_REVERSA_PROVISORIO': 13,
    'SAP_BAU_SUPRIMENTO': 14,
    'LAST_MILE_SUPRIMENTO_ERRO_INTEGRACAO': 15,
}

ENVIRONMENT_PROFILES = {
    'homolog': {
        'label': 'Homologação',
        'db_host': '192.168.0.219',
        'base_path': 'hg-arancia/',
        'api_url': 'http://192.168.0.216/homo-fulfillment',
        'stock_api_url': 'http://192.168.0.214/hg-stock/api',
        'transp_api_url': 'http://192.168.0.215/hg-api-transportes/api',
        'mural_api_url': 'http://192.168.0.214/hg-api-mural/api',
        'api_base': 'http://192.168.0.216/RetencaoAPI/api',
        'api_base_bko': 'http://192.168.0.214/hg-api-equipamentos/api/',
        'crm_api_base_url': 'http://192.168.0.214/hg-api-crm',
        'order_origin_ids': _ORDER_ORIGIN_IDS_HOMOLOG,
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
        'crm_api_base_url': 'http://192.168.0.214/api-crm',
        'order_origin_ids': _ORDER_ORIGIN_IDS_PROD,
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
    namespace['CRM_API_BASE_URL'] = profile['crm_api_base_url']
    namespace['CRM_API_V1_STR'] = '/api/v1'

    for key, origin_id in profile.get('order_origin_ids', {}).items():
        namespace[f'ORDER_ORIGIN_{key}'] = origin_id

    if 'DATABASES' in namespace and isinstance(namespace['DATABASES'], dict):
        default_db = namespace['DATABASES'].get('default')
        if isinstance(default_db, dict):
            default_db['HOST'] = profile['db_host']
