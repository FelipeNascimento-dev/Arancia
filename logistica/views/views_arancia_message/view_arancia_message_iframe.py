from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from logistica.services.arancia_message_service import (
    AranciaMessageAuthError,
    build_arancia_message_iframe_url,
    can_embed_arancia_message,
)


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def arancia_message_iframe(request):
    context = {
        'arancia_message_url': None,
        'arancia_message_error': None,
        'arancia_message_embed_allowed': False,
        'arancia_message_origin': f"{request.scheme}://{request.get_host()}",
    }

    try:
        context['arancia_message_url'] = build_arancia_message_iframe_url(request)
        context['arancia_message_embed_allowed'] = can_embed_arancia_message(request)
    except AranciaMessageAuthError as exc:
        context['arancia_message_error'] = str(exc)

    return render(
        request,
        'logistica/templates_arancia_message/arancia_message_iframe.html',
        context,
    )
