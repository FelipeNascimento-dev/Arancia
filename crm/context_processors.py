from crm.decorators import user_has_any_crm_perm
from crm.services.client import CrmApiClient
from crm.services.context import get_cached_me_context, get_user_gai_id
from crm.services.exceptions import CrmApiError


def crm_context(request):
    """Expõe GET /me/context com cache curto em sessão para menu e boards."""
    if not request.user.is_authenticated:
        return {}

    if not user_has_any_crm_perm(request.user):
        return {'crm_me_context': None}

    if get_user_gai_id(request.user) is None:
        return {
            'crm_me_context': None,
            'crm_missing_gai': True,
        }

    try:
        me_context = get_cached_me_context(
            request,
            client_factory=lambda: CrmApiClient(request.user),
        )
        return {'crm_me_context': me_context}
    except CrmApiError:
        return {'crm_me_context': None, 'crm_context_error': True}
