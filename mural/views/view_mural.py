from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages

from logistica.models import GroupAditionalInformation
from setup.local_settings import MURAL_API_URL
from utils.request import RequestClient

from datetime import datetime


ITEM_TYPE_LABELS = {
    "announcement": "Comunicado",
    "notice": "Aviso",
    "script": "Script",
    "manual": "Manual",
}

SEVERITY_LABELS = {
    "informational": "Informativo",
    "moderate": "Moderado",
    "important": "Importante",
    "critical": "Crítico",
}


def format_datetime(value):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return value


def normalize_item(item):
    return {
        "id": item.get("id"),
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "content": item.get("content", ""),
        "item_type": item.get("item_type", "notice"),
        "item_type_label": ITEM_TYPE_LABELS.get(
            item.get("item_type"), item.get("item_type", "Item").title()
        ),
        "severity": item.get("severity", "informational"),
        "severity_label": SEVERITY_LABELS.get(
            item.get("severity"), item.get("severity", "Informativo").title()
        ),
        "starts_at": format_datetime(item.get("starts_at")),
        "ends_at": format_datetime(item.get("ends_at")),
        "until_read": item.get("until_read", False),
        "is_indefinite": item.get("is_indefinite", False),
        "is_pinned": item.get("is_pinned", False),
        "is_active": item.get("is_active", True),
        "is_read": item.get("is_read", item.get("read", False)),
        "link": item.get("external_link") or item.get("attachment_url") or item.get("image_url") or "#",
        "external_link": item.get("external_link") or "",
        "attachment_url": item.get("attachment_url") or "",
        "image_url": item.get("image_url") or "",
        "target_type": item.get("target_type") or "",
        "created_by_id": item.get("created_by_id"),
    }


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def mural(request):
    mural_data = {"items": []}

    user_id = request.user.id
    gai_id = request.user.designacao.informacao_adicional_id

    User = get_user_model()

    target_users = list(
        User.objects.filter(
            username__istartswith="ARC"
        )
        .order_by("username")
        .values("id", "username", "first_name", "last_name")
    )

    target_groups = list(
        GroupAditionalInformation.objects.all()
        .order_by("nome")
        .values("id", "nome")
    )

    try:
        url = (
            f"{MURAL_API_URL}/v1/items/by-user/"
            f"?user_id={user_id}&gai_id={gai_id}"
        )

        client = RequestClient(
            url=url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        resp = client.send_api_request()

        if isinstance(resp, dict) and 'detail' in resp:
            messages.error(request, resp.get('detail'))

        if isinstance(resp, list):
            items = resp
        elif isinstance(resp, dict):
            items = (
                resp.get("items")
                or resp.get("results")
                or resp.get("data")
                or []
            )
        else:
            items = []

        mural_data["items"] = [normalize_item(item) for item in items]

    except Exception as e:
        messages.warning(
            request, f"Não foi possível carregar os itens do mural. Erro: {e}"
        )

    if "create_mural_item" in request.POST:
        messages.info(
            request, "Funcionalidade de criação de item ainda não implementada.")

    return render(request, 'mural/template_mural.html', {
        'site_title': 'Home',
        'current_menu': 'home',
        'mural_data': mural_data,
        'target_users': target_users,
        'target_groups': target_groups,
    })
