from urllib.parse import urlencode

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import requests
import json
from pathlib import Path
from setup.local_settings import MURAL_API_URL, TRANSP_API_URL
from mural.helpers.create_item_payload import build_create_item_v2_payload
from mural.helpers.form_draft import extract_create_form_draft, extract_created_item_id
from mural.helpers.mural_api import (
    fetch_mural_items_for_user_raw,
    merge_author_items_missing_from_feed,
    merge_pending_item_for_creator,
)
from mural.helpers.target_catalogs import empty_target_catalogs, get_mural_target_catalogs
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


def build_attachments_from_files(uploaded_files, descriptions=None):
    attachments = []
    descriptions = descriptions or []

    for index, uploaded_file in enumerate(uploaded_files):
        if not uploaded_file:
            continue

        file_url = upload_file_to_firebase(uploaded_file)

        file_name = uploaded_file.name
        file_extension = Path(
            uploaded_file.name).suffix.replace(".", "").lower()

        file_description = ""

        if index < len(descriptions):
            file_description = descriptions[index] or ""

        attachments.append(
            {
                "file_name": file_name,
                "file_url": file_url,
                "file_extension": file_extension,
                "file_description": file_description,
            }
        )

    return attachments


SUMMARY_MAX_CHARS = 500


def validate_summary_length(summary):
    if not summary:
        return True, None

    char_count = len(summary)
    if char_count > SUMMARY_MAX_CHARS:
        return False, (
            f"O resumo não pode ter mais de {SUMMARY_MAX_CHARS} caracteres "
            f"(atual: {char_count})."
        )

    return True, None


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


def _normalize_reads_param(raw_value):
    reads_param = (raw_value or "false").lower()
    if reads_param not in ("true", "false"):
        return "false"
    return reads_param


def fetch_mural_items_for_user(
    user_id,
    gai_id,
    reads_param="false",
    *,
    pending_item_id=None,
    include_author_orphans=False,
):
    """Busca itens do feed consumidor na API do mural."""
    items = fetch_mural_items_for_user_raw(
        user_id=user_id,
        gai_id=gai_id,
        reads_param=reads_param,
    )

    items = merge_pending_item_for_creator(
        items,
        pending_item_id=pending_item_id,
        user_id=user_id,
    )

    if include_author_orphans:
        items = merge_author_items_missing_from_feed(items, user_id=user_id)

    return [normalize_item(item) for item in items]


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def mural_items_feed(request):
    """JSON do feed — carregado pelo browser após o shell da página."""
    reads_param = _normalize_reads_param(request.GET.get("reads"))
    pending_item_id = request.GET.get("pending_id") or request.session.get(
        "mural_pending_item_id"
    )

    try:
        items = fetch_mural_items_for_user(
            user_id=request.user.id,
            gai_id=request.user.designacao.informacao_adicional_id,
            reads_param=reads_param,
            pending_item_id=pending_item_id,
            include_author_orphans=request.user.has_perm("mural.ger_mural"),
        )
    except Exception as exc:
        return JsonResponse(
            {"items": [], "error": str(exc)},
            status=502,
        )

    return JsonResponse({"items": items})


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def mural(request):
    mural_data = {"items": []}
    view_read_results = []
    view_read_search_done = False
    view_read_selected_item_id = ""
    view_read_filters = {
        "username": "",
        "name": "",
        "gai_id": "",
        "limit": "20",
        "all_results": False,
    }

    user_id = request.user.id
    gai_id = request.user.designacao.informacao_adicional_id

    if request.user.has_perm("mural.ger_mural"):
        target_users, target_groups, target_gais = get_mural_target_catalogs()
    else:
        target_users, target_groups, target_gais = empty_target_catalogs()

    reads_param = _normalize_reads_param(request.GET.get("reads"))
    show_reads = reads_param == "true"
    create_form_draft = None
    mural_pending_item_id = request.session.pop("mural_pending_item_id", None)

    if "view_reads" in request.POST:
        view_read_search_done = True

        view_item_id = request.POST.get("item_id")
        view_username = request.POST.get("username", "").strip()
        view_name = request.POST.get("name", "").strip()
        view_gai_id = request.POST.get("gai_id", "").strip()
        view_limit = request.POST.get("limit", "").strip()
        view_all_results = request.POST.get("all_results") == "on"

        view_read_selected_item_id = view_item_id

        view_read_filters = {
            "username": view_username,
            "name": view_name,
            "gai_id": view_gai_id,
            "limit": view_limit,
            "all_results": view_all_results,
        }

        params = {
            "skip": 0,
        }

        if not view_all_results:
            params["limit"] = view_limit or "20"

        if view_username:
            params["username"] = view_username

        if view_name:
            params["name"] = view_name

        if view_gai_id:
            params["gai_id"] = view_gai_id

        query_string = urlencode(params)

        try:
            view_read_url = (
                f"{MURAL_API_URL}/v1/item-reads/by-item-id/{view_item_id}"
                f"?{query_string}"
            )

            view_read_client = RequestClient(
                url=view_read_url,
                method="GET",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

            view_read_resp = view_read_client.send_api_request()

            if isinstance(view_read_resp, dict) and "detail" in view_read_resp:
                messages.error(request, view_read_resp.get("detail"))
                view_read_results = []

            elif isinstance(view_read_resp, list):
                view_read_results = view_read_resp

            elif isinstance(view_read_resp, dict):
                view_read_results = (
                    view_read_resp.get("items")
                    or view_read_resp.get("results")
                    or view_read_resp.get("data")
                    or []
                )

            else:
                view_read_results = []

            view_read_results = [
                normalize_reader(reader)
                for reader in view_read_results
            ]

        except Exception as e:
            messages.warning(
                request,
                f"Não foi possível carregar os leitores do item. Erro: {e}"
            )
            view_read_results = []

    if "create_mural_item" in request.POST:
        def _store_create_draft_on_error(message):
            nonlocal create_form_draft
            messages.error(request, message)
            create_form_draft = extract_create_form_draft(request.POST)
            if request.FILES.getlist("attachment_files") or request.FILES.get("image_file"):
                messages.warning(
                    request,
                    "Os arquivos selecionados precisam ser anexados novamente.",
                )

        summary = request.POST.get("summary")
        severity = request.POST.get("severity")
        starts_at_raw = request.POST.get("starts_at")
        ends_at_raw = request.POST.get("ends_at")

        is_valid_summary, summary_error = validate_summary_length(summary)
        if not is_valid_summary:
            _store_create_draft_on_error(summary_error)
        else:
            is_valid_critical, critical_error = validate_critical_duration(
                severity=severity,
                starts_at_raw=starts_at_raw,
                ends_at_raw=ends_at_raw
            )

            if not is_valid_critical:
                _store_create_draft_on_error(critical_error)
            else:
                attachment_files = request.FILES.getlist("attachment_files")
                attachment_descriptions = request.POST.getlist(
                    "attachment_descriptions")

                image_file = request.FILES.get("image_file")

                attachments = []
                image_url = None

                try:
                    if attachment_files:
                        attachments = build_attachments_from_files(
                            uploaded_files=attachment_files,
                            descriptions=attachment_descriptions
                        )

                    if image_file:
                        image_url = upload_file_to_firebase(image_file)

                except Exception as e:
                    _store_create_draft_on_error(
                        f"Erro ao enviar arquivo/imagem para o Firebase. Erro: {e}"
                    )
                else:
                    payload, target_error = build_create_item_v2_payload(
                        post_data=request.POST,
                        user_id=request.user.id,
                        attachments=attachments,
                        image_url=image_url,
                    )

                    if target_error:
                        _store_create_draft_on_error(target_error)
                    else:
                        try:
                            create_url = (
                                f"{MURAL_API_URL}/v2/items/create-item/"
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

                            if isinstance(create_resp, dict) and 'detail' in create_resp:
                                _store_create_draft_on_error(create_resp.get('detail'))
                            else:
                                created_id = extract_created_item_id(create_resp)
                                if created_id is not None:
                                    request.session["mural_pending_item_id"] = created_id
                                    try:
                                        visible_items = fetch_mural_items_for_user(
                                            user_id=request.user.id,
                                            gai_id=request.user.designacao.informacao_adicional_id,
                                            reads_param="false",
                                        )
                                        visible_ids = {
                                            str(item.get("id"))
                                            for item in visible_items
                                        }
                                        if str(created_id) not in visible_ids:
                                            target_type = payload.get("target_type")
                                            if target_type == "custom":
                                                messages.warning(
                                                    request,
                                                    "Item criado, mas ainda não está visível no "
                                                    "seu feed. Verifique se o público "
                                                    "personalizado inclui seu usuário, grupo ou "
                                                    "GAI. Você pode ajustar o item em "
                                                    "Gerenciamento do mural.",
                                                )
                                            else:
                                                messages.warning(
                                                    request,
                                                    "Item criado, mas ainda não apareceu no feed. "
                                                    "Aguarde alguns segundos e atualize a página.",
                                                )
                                    except Exception:
                                        pass
                                messages.success(request, "Item criado com sucesso!")
                                return redirect('mural:mural')

                        except Exception as e:
                            _store_create_draft_on_error(
                                f"Erro ao criar item no mural. Erro: {e}"
                            )

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

        is_valid_summary, summary_error = validate_summary_length(edit_summary)
        if not is_valid_summary:
            messages.error(request, summary_error)
            return redirect('mural:mural')

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
        current_image_url = request.POST.get("current_image_url") or None

        current_attachments_raw = request.POST.get(
            "current_attachments") or "[]"

        try:
            current_attachments = json.loads(current_attachments_raw)

            if not isinstance(current_attachments, list):
                current_attachments = []

        except Exception:
            current_attachments = []

        removed_attachment_urls = request.POST.getlist("remove_attachment_url")

        if removed_attachment_urls:
            current_attachments = [
                attachment
                for attachment in current_attachments
                if attachment.get("file_url") not in removed_attachment_urls
            ]

        edit_attachment_files = request.FILES.getlist("attachment_files")
        edit_attachment_descriptions = request.POST.getlist(
            "attachment_descriptions")

        edit_image_file = request.FILES.get("image_file")

        edit_attachments = current_attachments
        edit_image_url = current_image_url

        try:
            if edit_attachment_files:
                new_attachments = build_attachments_from_files(
                    uploaded_files=edit_attachment_files,
                    descriptions=edit_attachment_descriptions
                )

                edit_attachments.extend(new_attachments)

            if edit_image_file:
                edit_image_url = upload_file_to_firebase(edit_image_file)

        except Exception as e:
            messages.error(
                request, f"Erro ao enviar novo arquivo/imagem para o Firebase. Erro: {e}"
            )
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
            "attachments": edit_attachments,
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
        'view_read_results': view_read_results,
        'view_read_search_done': view_read_search_done,
        'view_read_selected_item_id': view_read_selected_item_id,
        'view_read_filters': view_read_filters,
        'show_reads': show_reads,
        'create_form_draft': create_form_draft,
        'mural_pending_item_id': mural_pending_item_id,
    })
