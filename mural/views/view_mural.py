from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages
import requests
from logistica.models import GroupAditionalInformation, Group
from setup.local_settings import MURAL_API_URL, TRANSP_API_URL
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


def normalize_item(item, read_item_ids=None):
    read_item_ids = read_item_ids or set()

    item_id = item.get("id")

    try:
        item_id_int = int(item_id)
    except Exception:
        item_id_int = None

    is_read_from_item = item.get("is_read", item.get("read", False))
    is_read_from_endpoint = item_id_int in read_item_ids if item_id_int is not None else False

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

        "is_read": bool(is_read_from_item or is_read_from_endpoint),

        "link": item.get("external_link") or item.get("attachment_url") or item.get("image_url") or "#",
        "external_link": item.get("external_link") or "",
        "attachment_url": item.get("attachment_url") or "",
        "image_url": item.get("image_url") or "",
        "target_type": item.get("target_type") or "",
        "created_by_id": item.get("created_by_id"),
    }


def upload_file_to_firebase(uploaded_file):
    if not uploaded_file:
        return None

    upload_url = f"{TRANSP_API_URL}/v2/firebase/upload/Firebase/"

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.file,
            uploaded_file.content_type
        )
    }

    response = requests.post(
        upload_url,
        files=files,
        timeout=60
    )

    try:
        response_data = response.json()
    except Exception:
        raise Exception(
            f"Erro ao interpretar resposta do upload: {response.text}")

    if response.status_code not in [200, 201]:
        raise Exception(response_data)

    firebase_url = (
        response_data.get("url")
        or response_data.get("file_url")
        or response_data.get("download_url")
        or response_data.get("public_url")
        or response_data.get("data", {}).get("url")
    )

    if not firebase_url:
        raise Exception(
            f"Upload realizado, mas nenhuma URL foi retornada: {response_data}")

    return firebase_url


def validate_critical_duration(severity, starts_at_raw, ends_at_raw):
    if severity != "critical":
        return True, None

    if not starts_at_raw or not ends_at_raw:
        return False, "Item crítico precisa ter data de início e data de fim."

    try:
        starts_dt = datetime.strptime(starts_at_raw, "%Y-%m-%dT%H:%M")
        ends_dt = datetime.strptime(ends_at_raw, "%Y-%m-%dT%H:%M")
    except Exception:
        return False, "Datas inválidas para o item crítico."

    if ends_dt <= starts_dt:
        return False, "A data final precisa ser maior que a data inicial."

    max_end_dt = starts_dt + timedelta(days=7)

    if ends_dt > max_end_dt:
        return False, "Item crítico pode ter duração máxima de 7 dias."

    return True, None


def get_read_item_ids_by_user(user_id):
    try:
        item_read_url = f"{MURAL_API_URL}/v1/item-reads/by-user/{user_id}"

        item_read_client = RequestClient(
            url=item_read_url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        item_read_resp = item_read_client.send_api_request()

        if isinstance(item_read_resp, list):
            reads = item_read_resp
        elif isinstance(item_read_resp, dict):
            reads = (
                item_read_resp.get("items")
                or item_read_resp.get("results")
                or item_read_resp.get("data")
                or []
            )
        else:
            reads = []

        read_ids = set()

        for read in reads:
            mural_item_id = read.get("mural_item_id")

            if mural_item_id is not None:
                read_ids.add(int(mural_item_id))

        return read_ids

    except Exception:
        return set()


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

    target_gais = list(
        GroupAditionalInformation.objects.all()
        .order_by("nome")
        .values("id", "nome")
    )

    target_groups = list(
        Group.objects.filter(
            name__istartswith="arancia_"
        )
        .order_by("name")
        .values("id", "name")
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

        read_item_ids = get_read_item_ids_by_user(user_id)

        mural_data["items"] = [
            normalize_item(item, read_item_ids=read_item_ids)
            for item in items
        ]

    except Exception as e:
        messages.warning(
            request, f"Não foi possível carregar os itens do mural. Erro: {e}"
        )

    if "create_mural_item" in request.POST:
        title = request.POST.get("title")
        summary = request.POST.get("summary")
        content = request.POST.get("content")
        item_type = request.POST.get("item_type")
        severity = request.POST.get("severity")
        target_type = request.POST.get("target_type")

        is_active = request.POST.get("is_active") == "on"
        is_pinned = request.POST.get("is_pinned") == "on"
        is_indefinite = request.POST.get("is_indefinite") == "on"
        until_read = request.POST.get("until_read") == "on"

        starts_at_raw = request.POST.get("starts_at")
        ends_at_raw = request.POST.get("ends_at")

        is_valid_critical, critical_error = validate_critical_duration(
            severity=severity,
            starts_at_raw=starts_at_raw,
            ends_at_raw=ends_at_raw
        )

        if not is_valid_critical:
            messages.error(request, critical_error)
            return redirect('mural:mural')

        starts_at = format_datetime_to_api(starts_at_raw)
        ends_at = format_datetime_to_api(ends_at_raw)

        external_link = request.POST.get("external_link") or None

        attachment_file = request.FILES.get("attachment_file")
        image_file = request.FILES.get("image_file")

        attachment_url = None
        image_url = None

        try:
            if attachment_file:
                attachment_url = upload_file_to_firebase(attachment_file)

            if image_file:
                image_url = upload_file_to_firebase(image_file)

        except Exception as e:
            messages.error(
                request, f"Erro ao enviar arquivo/imagem para o Firebase. Erro: {e}")
            return redirect('mural:mural')

        created_by_id = request.user.id

        target_ids = request.POST.getlist("target_id")

        if target_type == "all":
            ids = []
        else:
            ids = [
                int(target_id)
                for target_id in target_ids
                if str(target_id).strip().isdigit()
            ]

        payload = {
            "title": title,
            "summary": summary,
            "content": content,
            "item_type": item_type,
            "severity": severity,
            "target_type": target_type,
            "is_active": is_active,
            "is_pinned": is_pinned,
            "is_indefinite": is_indefinite,
            "until_read": until_read,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "external_link": external_link,
            "attachment_url": attachment_url,
            "image_url": image_url,
            "created_by_id": created_by_id,
            "ids": ids
        }

        print("STARTS POST HTML:", request.POST.get("starts_at"))
        print("STARTS API:", starts_at)
        print("ENDS POST HTML:", request.POST.get("ends_at"))
        print("ENDS API:", ends_at)

        try:
            create_url = (
                f"{MURAL_API_URL}/v1/items/create-item/"
            )

            create_client = RequestClient(
                url=create_url,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                request_data=payload
            )

            create_resp = create_client.send_api_request()

            if 'detail' in create_resp:
                messages.error(request, create_resp.get('detail'))
            else:
                messages.success(request, "Item criado com sucesso!")
                return redirect('mural:mural')

        except Exception as e:
            messages.error(request, f"Erro ao criar item no mural. Erro: {e}")

    if "disable_item" in request.POST:
        item_id = request.POST.get("disable_item_id")

        try:
            disable_url = (
                f"{MURAL_API_URL}/v1/items/disable-item/{item_id}"
            )

            disable_client = RequestClient(
                url=disable_url,
                method="DELETE",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

            disable_resp = disable_client.send_api_request()

            if 'detail' in disable_resp:
                messages.error(request, disable_resp.get('detail'))
            else:
                messages.success(request, "Item desabilitado com sucesso!")
                return redirect('mural:mural')

        except Exception as e:
            messages.error(
                request, f"Erro ao desabilitar item no mural. Erro: {e}")

    if "mark_read_item" in request.POST:
        mark_read_item_id = request.POST.get("mark_read_item_id")
        mark_read_user_id = request.user.id

        mark_read_payload = {
            "mural_item_id": mark_read_item_id,
            "user_id": mark_read_user_id
        }

        try:
            mark_read_url = (
                f"{MURAL_API_URL}/v1/item-reads/?manualconfirmation=true"
            )

            mark_read_client = RequestClient(
                url=mark_read_url,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                request_data=mark_read_payload
            )

            mark_read_resp = mark_read_client.send_api_request()

            if 'detail' in mark_read_resp:
                messages.error(request, mark_read_resp.get('detail'))
            else:
                messages.success(
                    request, "Item marcado como lido com sucesso!")
                return redirect('mural:mural')

        except Exception as e:
            messages.warning(
                request, f"Não foi possível marcar o item como lido. Erro: {e}"
            )

    if "edit_mural_item" in request.POST:
        edit_item_id = request.POST.get("edit_item_id")

        edit_title = request.POST.get("title")
        edit_summary = request.POST.get("summary")
        edit_content = request.POST.get("content")
        edit_item_type = request.POST.get("item_type")
        edit_severity = request.POST.get("severity")

        edit_is_active = request.POST.get("is_active") == "on"
        edit_is_pinned = request.POST.get("is_pinned") == "on"
        edit_is_indefinite = request.POST.get("is_indefinite") == "on"
        edit_until_read = request.POST.get("until_read") == "on"

        edit_starts_at_raw = request.POST.get("starts_at")
        edit_ends_at_raw = request.POST.get("ends_at")

        is_valid_critical, critical_error = validate_critical_duration(
            severity=edit_severity,
            starts_at_raw=edit_starts_at_raw,
            ends_at_raw=edit_ends_at_raw
        )

        if not is_valid_critical:
            messages.error(request, critical_error)
            return redirect('mural:mural')

        edit_starts_at = format_datetime_to_api(edit_starts_at_raw)
        edit_ends_at = format_datetime_to_api(edit_ends_at_raw)

        edit_external_link = request.POST.get("external_link") or None
        current_attachment_url = request.POST.get(
            "current_attachment_url") or None
        current_image_url = request.POST.get("current_image_url") or None

        edit_attachment_file = request.FILES.get("attachment_file")
        edit_image_file = request.FILES.get("image_file")

        edit_attachment_url = current_attachment_url
        edit_image_url = current_image_url

        try:
            if edit_attachment_file:
                edit_attachment_url = upload_file_to_firebase(
                    edit_attachment_file)

            if edit_image_file:
                edit_image_url = upload_file_to_firebase(edit_image_file)

        except Exception as e:
            messages.error(
                request, f"Erro ao enviar novo arquivo/imagem para o Firebase. Erro: {e}")
            return redirect('mural:mural')

        edit_payload = {
            "title": edit_title,
            "summary": edit_summary,
            "content": edit_content,
            "item_type": edit_item_type,
            "severity": edit_severity,
            "is_active": edit_is_active,
            "is_pinned": edit_is_pinned,
            "is_indefinite": edit_is_indefinite,
            "until_read": edit_until_read,
            "starts_at": edit_starts_at,
            "ends_at": edit_ends_at,
            "external_link": edit_external_link,
            "attachment_url": edit_attachment_url,
            "image_url": edit_image_url,
            "updated_by_id": request.user.id,
        }

        try:
            edit_url = (
                f"{MURAL_API_URL}/v1/items/update-item/{edit_item_id}"
            )

            edit_client = RequestClient(
                url=edit_url,
                method="PUT",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                request_data=edit_payload
            )

            edit_resp = edit_client.send_api_request()

            if 'detail' in edit_resp:
                messages.error(request, edit_resp.get('detail'))
            else:
                messages.success(request, "Item editado com sucesso!")
                return redirect('mural:mural')

        except Exception as e:
            messages.error(
                request, f"Erro ao editar item no mural. Erro: {e}")

    return render(request, 'mural/template_mural.html', {
        'site_title': 'Home',
        'current_menu': 'home',
        'mural_data': mural_data,
        'target_users': target_users,
        'target_gais': target_gais,
        'target_groups': target_groups,
    })
