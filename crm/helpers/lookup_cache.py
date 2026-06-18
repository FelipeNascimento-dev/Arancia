"""Cache request-scoped e Redis para catálogos/respostas CRM."""

from __future__ import annotations

import hashlib
import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CRM_LOOKUPS_CACHE_ATTR = "_crm_lookups_cache"


def _lookups_cache(request):
    if request is None:
        return None
    mem = getattr(request, CRM_LOOKUPS_CACHE_ATTR, None)
    if mem is None:
        mem = {}
        setattr(request, CRM_LOOKUPS_CACHE_ATTR, mem)
    return mem


def _redis_cache_enabled() -> bool:
    return bool(getattr(settings, "CRM_REDIS_CACHE_ENABLED", True))


def _redis_ttl() -> int:
    return int(getattr(settings, "CRM_LOOKUPS_REDIS_CACHE_TTL", 300))


def _redis_key(key: str) -> str:
    """Prefixo por ambiente para evitar colisão entre homolog/prod."""
    env = getattr(settings, "ENVIRONMENT", "default")
    base = getattr(settings, "CRM_API_BASE_URL", "") or "crm"
    digest = hashlib.md5(base.encode("utf-8")).hexdigest()[:8]
    return f"crm:{env}:{digest}:{key}"


def _safe_cache_get(key: str):
    if not _redis_cache_enabled():
        return None
    try:
        return cache.get(_redis_key(key))
    except Exception:
        logger.debug("CRM cache get falhou para %s", key, exc_info=True)
        return None


def _safe_cache_set(key: str, value, ttl: int) -> None:
    if not _redis_cache_enabled():
        return
    try:
        cache.set(_redis_key(key), value, ttl)
    except Exception:
        logger.debug("CRM cache set falhou para %s", key, exc_info=True)


def get_cached_lookup(request, key, loader, *, redis_key=None, redis_ttl=None):
    """
    Memoiza resultado de loader() por chave durante o request.

    Com ``redis_key``, também persiste em Redis (TTL configurável) para
    reutilização entre requests.
    """
    mem = _lookups_cache(request)
    if mem is not None and key in mem:
        return mem[key]

    rk = redis_key or key
    cached = _safe_cache_get(rk)
    if cached is not None:
        if mem is not None:
            mem[key] = cached
        return cached

    value = loader()
    if mem is not None:
        mem[key] = value
    _safe_cache_set(rk, value, redis_ttl if redis_ttl is not None else _redis_ttl())
    return value


def get_cached_lookup_for_client(client, key, loader, *, redis_key=None, redis_ttl=None):
    """Atalho quando só há CrmApiClient (usa client.request)."""
    request = getattr(client, "request", None)
    return get_cached_lookup(
        request,
        key,
        loader,
        redis_key=redis_key,
        redis_ttl=redis_ttl,
    )


def get_user_scoped_lookup(request, key, loader, *, redis_ttl=None):
    """Cache Redis por usuário (ex.: /me/context)."""
    if not request or not getattr(request, "user", None) or not request.user.is_authenticated:
        return loader()
    user_id = request.user.pk
    redis_key = f"user:{user_id}:{key}"
    return get_cached_lookup(
        request,
        key,
        loader,
        redis_key=redis_key,
        redis_ttl=redis_ttl,
    )
