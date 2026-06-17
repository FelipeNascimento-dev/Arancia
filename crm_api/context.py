from __future__ import annotations

import base64

from django.conf import settings

from crm_api.exceptions import CrmAuthError
from crm_api.session_credentials import get_password_from_session


def build_basic_token(username: str, password: str) -> str:
    raw = f"{username}:{password}".encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def build_crm_headers(*, user, password: str, api_key: str | None = None) -> dict[str, str]:
    if not user or not user.is_authenticated:
        raise CrmAuthError("Usuário não autenticado.")
    if not password:
        raise CrmAuthError("Senha indisponível para Basic Auth.")
    key = api_key or getattr(settings, "CRM_API_KEY", "")
    if not key:
        raise CrmAuthError("CRM_API_KEY não configurada.")
    return {
        "Authorization": f"Basic {build_basic_token(user.username, password)}",
        "X-API-Key": key,
    }


def build_crm_headers_from_request(request) -> dict[str, str]:
    password = get_password_from_session(request)
    if password is None:
        raise CrmAuthError("Senha não encontrada na sessão — refaça o login.")
    return build_crm_headers(user=request.user, password=password)


def build_service_user_headers() -> dict[str, str]:
    from django.contrib.auth import get_user_model

    username = getattr(settings, "CRM_SERVICE_USERNAME", "") or ""
    password = getattr(settings, "CRM_SERVICE_PASSWORD", "") or ""
    if not username or not password:
        raise CrmAuthError("CRM_SERVICE_USERNAME/PASSWORD não configurados.")
    user = get_user_model().objects.get(username=username)
    return build_crm_headers(user=user, password=password)


def build_scheduler_headers() -> dict[str, str]:
    secret = getattr(settings, "CRM_INTERNAL_API_SECRET", "") or ""
    if not secret:
        raise CrmAuthError("CRM_INTERNAL_API_SECRET não configurado.")
    return {"Authorization": f"Bearer {secret}"}
