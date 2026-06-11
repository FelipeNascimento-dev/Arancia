"""Gates GAI reutilizáveis nas views CRM."""

from django.http import JsonResponse
from django.shortcuts import render

from .context import get_user_gai_id


def require_gai_or_render(
    request,
    template,
    *,
    site_title,
    menu_context=None,
    extra_context=None,
):
    """
    Retorna HttpResponse com alerta se usuário sem GAI; None se OK para prosseguir.
    """
    if get_user_gai_id(request.user) is not None:
        return None
    context = {
        'site_title': site_title,
        'missing_gai': True,
        **(menu_context or {}),
        **(extra_context or {}),
    }
    return render(request, template, context)


def ajax_require_gai(request):
    """Retorna JsonResponse de erro se usuário sem GAI; None se OK."""
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)
    return None
