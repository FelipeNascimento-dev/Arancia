from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from urllib.parse import urlparse

from logistica.services.arancia_message_service import (
    AranciaMessageAuthError,
    build_arancia_message_iframe_url,
    resolve_arancia_message_ui_base,
)


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def arancia_message_iframe(request):
    context = {
        'arancia_message_url': None,
        'arancia_message_error': None,
        'arancia_message_ui_host': '',
        "current_menu": "arancia_message_iframe",
        "site_title": "Messages"
    }

    try:
        context['arancia_message_url'] = build_arancia_message_iframe_url(request)
        ui_base = resolve_arancia_message_ui_base(request)
        context['arancia_message_ui_host'] = urlparse(ui_base).netloc or ui_base
    except AranciaMessageAuthError as exc:
        context['arancia_message_error'] = str(exc)

    return render(
        request,
        'logistica/templates_arancia_message/arancia_message_iframe.html',
        context
    )
