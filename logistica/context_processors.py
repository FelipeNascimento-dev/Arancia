from .models import UserProfile, AcompanhamentoSistema


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

    acompanhamentos = AcompanhamentoSistema.objects.filter(
        ativo=True
    ).order_by("ordem", "nome")

    return {
        "acompanhamentos_navbar": acompanhamentos
    }
