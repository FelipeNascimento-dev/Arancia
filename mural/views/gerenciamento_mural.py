
from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages
import requests
import json
from pathlib import Path
from logistica.models import GroupAditionalInformation, Group
from setup.local_settings import MURAL_API_URL, TRANSP_API_URL
from utils import request
from utils.request import RequestClient

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BR_TZ = ZoneInfo("America/Sao_Paulo")
UTC_TZ = ZoneInfo("UTC")


def parse_api_datetime(value):
    if not value:
        return None

    try:
        value = str(value).strip()

        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")

        dt = datetime.fromisoformat(value)

        # Se vier sem timezone da API, vamos assumir UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC_TZ)

        return dt

    except Exception:
        return None


def format_datetime(value):
    """
    API -> Tela
    Exemplo:
    2026-05-06T14:46:00.000Z -> 06/05/2026 11:46
    """
    dt = parse_api_datetime(value)

    if not dt:
        return value or ""

    dt_br = dt.astimezone(BR_TZ)

    return dt_br.strftime("%d/%m/%Y %H:%M")


def format_datetime_to_input(value):
    """
    API -> input datetime-local
    Exemplo:
    2026-05-06T14:46:00.000Z -> 2026-05-06T11:46
    """
    dt = parse_api_datetime(value)

    if not dt:
        return ""

    dt_br = dt.astimezone(BR_TZ)

    return dt_br.strftime("%Y-%m-%dT%H:%M")


def format_datetime_to_api(value):
    """
    input datetime-local -> API
    Exemplo:
    2026-05-06T11:46 -> 2026-05-06T14:46:00.000Z
    """
    if not value:
        return None

    try:
        dt_br = datetime.strptime(value, "%Y-%m-%dT%H:%M")
        dt_br = dt_br.replace(tzinfo=BR_TZ)

        dt_utc = dt_br.astimezone(UTC_TZ)

        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    except Exception:
        return None


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


def normalize_reader(reader):
    read_at_raw = (
        reader.get("read_at")
        or reader.get("created_at")
        or reader.get("updated_at")
    )

    return {
        **reader,
        "read_at_formatted": format_datetime(read_at_raw),
    }


def normalize_item(item):
    is_read_from_item = item.get("is_read", item.get("read", False))

    attachments = item.get("attachments") or []

    if not attachments and item.get("attachment_url"):
        attachments = [
            {
                "file_name": "Anexo",
                "file_url": item.get("attachment_url"),
                "file_extension": "",
                "file_description": "",
            }
        ]

    first_attachment_url = ""

    if attachments:
        first_attachment_url = attachments[0].get("file_url") or ""

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
        "starts_at_input": format_datetime_to_input(item.get("starts_at")),
        "ends_at_input": format_datetime_to_input(item.get("ends_at")),
        "until_read": item.get("until_read", False),
        "is_indefinite": item.get("is_indefinite", False),
        "is_pinned": item.get("is_pinned", False),
        "is_active": item.get("is_active", True),

        "is_read": bool(is_read_from_item),

        "link": item.get("external_link") or first_attachment_url or item.get("image_url") or "#",
        "external_link": item.get("external_link") or "",
        "attachments": attachments,
        "attachment_url": first_attachment_url,
        "image_url": item.get("image_url") or "",
        "target_type": item.get("target_type") or "",
        "created_by_id": item.get("created_by_id"),
    }


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def gerenciar_mural(request):
    mural_data = {"items": []}

    user_id = request.user.id

    try:
        params = {
            "created_by_id": user_id,
            "offset": 0,
            "limit": 200,
        }

        url = f"{MURAL_API_URL}/v1/items/by-created-by/?{urlencode(params)}"

        client = RequestClient(
            url=url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        resp = client.send_api_request()

        if isinstance(resp, dict) and "detail" in resp:
            messages.error(request, resp.get("detail"))

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

        mural_data["items"] = [
            normalize_item(item)
            for item in items
        ]

    except Exception as e:
        messages.warning(
            request,
            f"Não foi possível carregar os itens criados. Erro: {e}"
        )

    return render(request, "mural/gerenciamento_mural.html", {
        "site_title": "Gerenciar Mural",
        "current_menu": "mural",
        "mural_data": mural_data,
    })
