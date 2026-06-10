from django.contrib import messages


class CrmApiError(Exception):
    """Erro base na comunicação com a API CRM."""

    def __init__(self, message='Erro ao comunicar com o CRM.', *, status_code=None, detail=None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail or message


class CrmAuthError(CrmApiError):
    def __init__(self, message='Autenticação CRM inválida.', **kwargs):
        super().__init__(message, **kwargs)


class CrmForbiddenError(CrmApiError):
    def __init__(self, message='Sem permissão para esta ação no CRM.', **kwargs):
        super().__init__(message, **kwargs)


class CrmNotFoundError(CrmApiError):
    def __init__(self, message='Registro não encontrado no CRM.', **kwargs):
        super().__init__(message, **kwargs)


class CrmValidationError(CrmApiError):
    def __init__(self, message='Dados inválidos para o CRM.', **kwargs):
        super().__init__(message, **kwargs)


class CrmBusinessError(CrmApiError):
    def __init__(self, message='Operação não permitida no CRM.', **kwargs):
        super().__init__(message, **kwargs)


class CrmServerError(CrmApiError):
    def __init__(self, message='Erro interno no servidor CRM.', **kwargs):
        super().__init__(message, **kwargs)


class CrmConnectionError(CrmApiError):
    def __init__(self, message='Não foi possível conectar ao CRM.', **kwargs):
        super().__init__(message, **kwargs)


def _extract_detail(response):
    try:
        payload = response.json()
    except Exception:
        return response.text or 'Erro desconhecido'

    if isinstance(payload, dict):
        return payload.get('detail') or payload.get('message') or str(payload)
    if isinstance(payload, list):
        return str(payload)
    return str(payload)


def raise_for_status(response):
    if response.status_code < 400:
        return

    detail = _extract_detail(response)
    status = response.status_code
    kwargs = {'status_code': status, 'detail': detail}

    if status == 401:
        raise CrmAuthError(str(detail), **kwargs)
    if status == 403:
        raise CrmForbiddenError(str(detail), **kwargs)
    if status == 404:
        raise CrmNotFoundError(str(detail), **kwargs)
    if status == 400:
        raise CrmBusinessError(str(detail), **kwargs)
    if status == 422:
        raise CrmValidationError(str(detail), **kwargs)
    if status >= 500:
        raise CrmServerError(str(detail), **kwargs)
    raise CrmApiError(str(detail), **kwargs)


def handle_crm_error(request, exc):
    """Registra mensagem amigável em PT-BR para erros da API CRM."""
    if isinstance(exc, CrmAuthError):
        messages.error(request, 'Sessão CRM inválida. Faça login novamente.')
    elif isinstance(exc, CrmForbiddenError):
        messages.error(request, 'Você não tem permissão para esta ação no CRM.')
    elif isinstance(exc, CrmNotFoundError):
        messages.error(request, 'Registro não encontrado no CRM.')
    elif isinstance(exc, CrmValidationError):
        messages.error(request, f'Dados inválidos: {exc.detail}')
    elif isinstance(exc, CrmBusinessError):
        messages.error(request, str(exc.detail or exc))
    elif isinstance(exc, CrmConnectionError):
        messages.error(request, 'Não foi possível conectar ao CRM. Tente novamente.')
    elif isinstance(exc, CrmServerError):
        messages.error(request, 'Erro interno no CRM. Tente novamente mais tarde.')
    elif isinstance(exc, CrmApiError):
        messages.error(request, str(exc))
    else:
        messages.error(request, 'Erro inesperado ao acessar o CRM.')
