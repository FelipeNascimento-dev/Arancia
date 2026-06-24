"""Autenticação e URL do iframe Arancia Message (NinaBot)."""

from __future__ import annotations

from urllib.parse import urlencode

from django.conf import settings

from crm_api.session_credentials import get_password_from_session
from utils.request import RequestClient


class AranciaMessageAuthError(Exception):
    """Falha ao obter token para o iframe Arancia Message."""


def _extract_token(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("token", "access_token", "auth_token"):
        value = payload.get(key)
        if value:
            return str(value)
    data = payload.get("data")
    if isinstance(data, dict):
        return _extract_token(data)
    return None


def fetch_auth_token(*, username: str, password: str) -> str:
    url = getattr(settings, "ARANCIA_MESSAGE_AUTH_TOKEN_URL", "") or ""
    if not url:
        raise AranciaMessageAuthError("URL de autenticação do Arancia Message não configurada.")

    client = RequestClient(
        method="post",
        url=url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        request_data={
            "username": username,
            "password": password,
        },
        timeout=30,
    )
    data = client.send_api_request()

    if not isinstance(data, dict):
        raise AranciaMessageAuthError("Resposta inválida da API de autenticação.")

    token = _extract_token(data)
    if token:
        return token

    detail = data.get("detail")
    if isinstance(detail, list):
        detail = "; ".join(str(item) for item in detail)
    if detail:
        raise AranciaMessageAuthError(str(detail))

    message = data.get("message")
    if message:
        raise AranciaMessageAuthError(str(message))

    raise AranciaMessageAuthError("Token não retornado pela API de autenticação.")


def build_arancia_message_iframe_url(request) -> str:
    user = request.user
    if not user or not user.is_authenticated:
        raise AranciaMessageAuthError("Usuário não autenticado.")

    password = get_password_from_session(request)
    if not password:
        raise AranciaMessageAuthError(
            "Senha não encontrada na sessão — faça logout e login novamente para acessar o Arancia Message."
        )

    ui_base = (getattr(settings, "ARANCIA_MESSAGE_UI_URL", "") or "").rstrip("/")
    if not ui_base:
        raise AranciaMessageAuthError("URL do Arancia Message não configurada.")

    token = fetch_auth_token(username=user.username, password=password)
    return f"{ui_base}?{urlencode({'token': token})}"


def can_embed_arancia_message(request) -> bool:
    """
    O NinaBot só permite iframe de origens listadas em frame-ancestors (CSP).
    Homolog em IP interno precisa ser liberado no servidor do NinaBot.
    """
    allowed = getattr(settings, "ARANCIA_MESSAGE_FRAME_ANCESTORS", None)
    if not allowed:
        return True

    current = f"{request.scheme}://{request.get_host()}".rstrip("/")
    normalized = {origin.rstrip("/") for origin in allowed}
    return current in normalized
