"""Autenticação e URL do iframe Arancia Message (NinaBot)."""

from __future__ import annotations

from urllib.parse import urlencode, urlparse

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


def resolve_arancia_message_ui_base(request=None) -> str:
    """URL base da UI NinaBot. request reservado para escolha por ambiente no futuro."""
    del request
    return (getattr(settings, 'ARANCIA_MESSAGE_UI_URL', '') or '').rstrip('/')


def build_arancia_message_iframe_url(request) -> str:
    user = request.user
    if not user or not user.is_authenticated:
        raise AranciaMessageAuthError("Usuário não autenticado.")

    password = get_password_from_session(request)
    if not password:
        raise AranciaMessageAuthError(
            "Senha não encontrada na sessão — faça logout e login novamente para acessar o Arancia Message."
        )

    ui_base = resolve_arancia_message_ui_base(request)
    if not ui_base:
        raise AranciaMessageAuthError("URL do Arancia Message não configurada.")

    token = fetch_auth_token(username=user.username, password=password)
    return f"{ui_base}?{urlencode({'token': token})}"


def _origin_matches_frame_ancestor(current: str, allowed: str) -> bool:
    current = current.rstrip('/')
    allowed = allowed.rstrip('/')
    if current == allowed:
        return True

    cur = urlparse(current)
    alw = urlparse(allowed)
    if cur.scheme != alw.scheme or cur.hostname != alw.hostname:
        return False
    if alw.port is None:
        return True
    return cur.port == alw.port


def can_embed_arancia_message(request) -> bool:
    """
    Verifica se a origem do Arancia está na lista alinhada ao frame-ancestors do NinaBot.
    """
    allowed = getattr(settings, "ARANCIA_MESSAGE_FRAME_ANCESTORS", None)
    if not allowed:
        return True

    current = f"{request.scheme}://{request.get_host()}".rstrip("/")
    return any(_origin_matches_frame_ancestor(current, origin) for origin in allowed)
