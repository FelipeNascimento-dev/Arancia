"""Exceções tipadas para integração com a API CRM."""


class CrmApiError(Exception):
    def __init__(self, message, status_code=None, detail=None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(message)


class CrmConnectionError(CrmApiError):
    pass


class CrmNotFoundError(CrmApiError):
    pass


class CrmPermissionError(CrmApiError):
    pass


class CrmValidationError(CrmApiError):
    pass


class CrmAuthError(CrmApiError):
    pass


def crm_error_message_pt(exc):
    """Traduz exceções CRM para mensagens amigáveis em PT-BR."""
    if isinstance(exc, CrmAuthError):
        detail = str(exc.detail or exc.message or "").lower()
        if "senha não encontrada" in detail or "senha indisponível" in detail:
            return (
                "Senha do CRM não está na sessão. Faça logout e login novamente "
                "com sua senha de usuário (não use código de acesso temporário)."
            )
        if "crm_api_key" in detail:
            return "CRM_API_KEY não configurada no servidor. Contate o suporte."
        if exc.status_code == 401 or "credenciais" in detail:
            return (
                "A API CRM rejeitou usuário/senha. Confirme que seu login no Arancia "
                "usa a mesma senha cadastrada na API CRM e faça login novamente."
            )
        return "Sessão expirada ou credenciais inválidas para o CRM. Faça login novamente."
    if isinstance(exc, CrmConnectionError):
        return "Não foi possível conectar ao serviço CRM. Tente novamente mais tarde."
    if isinstance(exc, CrmNotFoundError):
        return "Registro não encontrado."
    if isinstance(exc, CrmPermissionError):
        return "Você não tem permissão para esta ação."
    if isinstance(exc, CrmValidationError):
        return exc.detail or "Dados inválidos. Verifique os campos informados."
    if isinstance(exc, CrmApiError):
        return exc.detail or "Erro ao processar solicitação no CRM."
    return "Erro inesperado ao comunicar com o CRM."
