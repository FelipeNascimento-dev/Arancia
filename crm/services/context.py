import time

from django.conf import settings

CRM_CONTEXT_SESSION_KEY = 'crm_me_context'
CRM_CONTEXT_TS_KEY = 'crm_me_context_ts'
CRM_CONTEXT_TTL_SECONDS = 300


def get_user_gai_id(user):
    """Retorna o ID do GAI da designação ou None se ausente."""
    designacao = getattr(user, 'designacao', None)
    if designacao is None:
        return None
    return designacao.informacao_adicional_id


def _designation_id(user):
    designacao = getattr(user, 'designacao', None)
    if designacao is None:
        return ''
    return str(designacao.id)


def build_crm_headers(user):
    """
    Monta headers X-CRM-* + Bearer para chamadas em nome do usuário logado.
    X-CRM-Designation-IDs: ID de logistica_userdesignation (OneToOne legado).
    """
    secret = settings.CRM_INTERNAL_API_SECRET
    group_ids = ','.join(str(g.id) for g in user.groups.all())

    headers = {
        'Authorization': f'Bearer {secret}',
        'Accept': 'application/json',
        'X-CRM-User-ID': str(user.id),
        'X-CRM-Username': user.username,
        'X-CRM-Designation-IDs': _designation_id(user),
        'X-CRM-Is-Superuser': 'true' if user.is_superuser else 'false',
        'X-CRM-Is-Staff': 'true' if user.is_staff else 'false',
        'X-CRM-Group-IDs': group_ids,
    }
    return headers


def build_service_crm_headers():
    """Headers para jobs internos (Celery) com usuário de serviço."""
    secret = settings.CRM_INTERNAL_API_SECRET
    return {
        'Authorization': f'Bearer {secret}',
        'Accept': 'application/json',
        'X-CRM-User-ID': str(settings.CRM_SERVICE_USER_ID),
        'X-CRM-Username': settings.CRM_SERVICE_USERNAME,
        'X-CRM-Designation-IDs': '',
        'X-CRM-Group-IDs': '',
    }


def invalidate_crm_session_cache(request):
    """Remove cache de /me/context da sessão (login/logout)."""
    if hasattr(request, 'session'):
        request.session.pop(CRM_CONTEXT_SESSION_KEY, None)
        request.session.pop(CRM_CONTEXT_TS_KEY, None)


def get_cached_me_context(request, *, client_factory):
    """
    Retorna contexto CRM da sessão ou busca GET /me/context.
    client_factory: callable que retorna CrmApiClient(request.user).
    """
    now = time.time()
    cached = request.session.get(CRM_CONTEXT_SESSION_KEY)
    cached_ts = request.session.get(CRM_CONTEXT_TS_KEY, 0)

    if cached is not None and (now - cached_ts) < CRM_CONTEXT_TTL_SECONDS:
        return cached

    client = client_factory()
    context = client.get('/me/context')
    request.session[CRM_CONTEXT_SESSION_KEY] = context
    request.session[CRM_CONTEXT_TS_KEY] = now
    return context
