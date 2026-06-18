from django.conf import settings
from django.core.cache import cache

from .models import UserProfile, AcompanhamentoSistema

ACOMPANHAMENTOS_NAVBAR_CACHE_KEY = "acompanhamentos_navbar:active"


def avatar_url(request):
    if not request.user.is_authenticated:
        return {"avatar_url": "/static/global/images/default-avatar.jpg"}

    perfil = getattr(request.user, "perfil", None)
    if perfil and perfil.avatar:
        return {"avatar_url": perfil.avatar}
    return {"avatar_url": "/static/global/images/default-avatar.jpg"}


def acompanhamentos_navbar(request):
    if not request.user.is_authenticated:
        return {
            "acompanhamentos_navbar": []
        }

    ttl = int(getattr(settings, "ACOMPANHAMENTOS_NAVBAR_CACHE_TTL", 600))
    cached = cache.get(ACOMPANHAMENTOS_NAVBAR_CACHE_KEY)
    if cached is not None:
        return {"acompanhamentos_navbar": cached}

    acompanhamentos = list(
        AcompanhamentoSistema.objects.filter(ativo=True).order_by("ordem", "nome")
    )
    cache.set(ACOMPANHAMENTOS_NAVBAR_CACHE_KEY, acompanhamentos, ttl)
    return {"acompanhamentos_navbar": acompanhamentos}
