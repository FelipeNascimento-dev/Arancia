from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)

SESSION_KEY = "_crm_api_pwd_enc"


def _fernet() -> Fernet:
    raw = settings.SECRET_KEY.encode("utf-8")
    key = base64.urlsafe_b64encode(raw.ljust(32, b"0")[:32])
    return Fernet(key)


def store_password_in_session(request: HttpRequest, password: str) -> None:
    request.session[SESSION_KEY] = _fernet().encrypt(password.encode("utf-8")).decode("ascii")
    request.session.modified = True


def get_password_from_session(request: HttpRequest) -> str | None:
    token = request.session.get(SESSION_KEY)
    if not token:
        return None
    try:
        return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken:
        logger.warning("CRM: token de senha na sessão inválido — refaça o login.")
        return None


def clear_password_from_session(request: HttpRequest) -> None:
    request.session.pop(SESSION_KEY, None)


@receiver(user_logged_in)
def _on_login(sender, request, user, **kwargs):
    from crm.context_processors import clear_crm_context_cache

    clear_crm_context_cache(request)
    password = getattr(request, "_crm_login_password", None)
    if password:
        store_password_in_session(request, password)


@receiver(user_logged_out)
def _on_logout(sender, request, user, **kwargs):
    from crm.context_processors import clear_crm_context_cache

    clear_password_from_session(request)
    if request is not None:
        clear_crm_context_cache(request)
