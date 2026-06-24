"""POST actions da Lista de Viagens (endpoints dedicados)."""

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from setup.local_settings import TRANSP_API_URL
from transportes.models import FiltroFavoritoUsuario
from transportes.services.lista_viagens_service import (
    SESSION_KEY_LISTA_VIAGENS_FILTROS,
    build_extract_params,
    montar_filtros_lista_viagens,
)
from transportes.services.transportes_metadata_service import (
    FILTRO_CAMPOS_LISTA_VIAGENS,
    build_tipos_status_maps,
    fetch_metadata,
)
from transportes.utils.filtros import obter_filtros_tela
from utils.request import RequestClient


def _filtros_da_sessao_ou_favorito(request):
    if SESSION_KEY_LISTA_VIAGENS_FILTROS in request.session:
        filtros = dict(request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS])
    else:
        filtros = obter_filtros_tela(
            request.user, FiltroFavoritoUsuario.TELA_LISTA_VIAGENS
        ) or {}
    filtros["Response"] = filtros.get("Response") or "resume"
    return filtros


def _maps_from_metadata():
    metadata = fetch_metadata()
    return build_tipos_status_maps(metadata["clientes_status"]), metadata


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def lista_viagens_export(request):
    if request.method != "POST":
        return redirect("transportes:lista_viagens")

    filtros = montar_filtros_lista_viagens(request.POST, FILTRO_CAMPOS_LISTA_VIAGENS)
    maps_ctx, _ = _maps_from_metadata()

    try:
        extract_params = build_extract_params(
            filtros,
            maps_ctx["tipo_api_map"],
            maps_ctx["status_api_map"],
        )
        url_extract = (
            f"{TRANSP_API_URL}/v2/order_travel/export/general/excel?"
            f"{urlencode(extract_params)}"
        )
        return redirect(url_extract)
    except Exception as e:
        messages.error(request, f"Erro ao extrair travels: {str(e)}")
        return redirect("transportes:lista_viagens")


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def lista_viagens_preparar_eventos(request):
    """Abre modal de criar eventos em lote — redireciona com flag na session."""
    if request.method != "POST":
        return redirect("transportes:lista_viagens")

    selected_travel_ids = request.POST.getlist("travels_selecionadas")
    if not selected_travel_ids:
        messages.error(request, "Selecione pelo menos uma viagem.")
        return redirect("transportes:lista_viagens")

    filtros = _filtros_da_sessao_ou_favorito(request)
    maps_ctx, metadata = _maps_from_metadata()
    resp = metadata["clientes_status"]

    client_id = request.POST.get("cliente") or filtros.get("cliente") or ""
    tipo_servico_id = request.POST.get("tipo_servico") or filtros.get("tipo_servico") or ""

    if isinstance(client_id, list):
        client_id = client_id[0] if client_id else ""
    client_id = str(client_id).strip()

    if isinstance(tipo_servico_id, list):
        tipo_servico_id = tipo_servico_id[0] if tipo_servico_id else ""
    tipo_servico_id = str(tipo_servico_id).strip()

    if tipo_servico_id.startswith("[") and tipo_servico_id.endswith("]"):
        tipo_servico_id = (
            tipo_servico_id.replace("[", "").replace("]", "")
            .replace("'", "").replace('"', "").strip()
        )

    travel_event_types = []
    cliente_nome = ""
    if client_id:
        for c in resp:
            if str(c.get("id")) == str(client_id):
                cliente_nome = c.get("nome") or c.get("name") or ""
                break

    order_type_api = maps_ctx["tipo_api_map"].get(tipo_servico_id, "") if tipo_servico_id else ""

    if cliente_nome and order_type_api:
        try:
            query = urlencode({
                "status": "true",
                "cliente": cliente_nome,
                "order_type": tipo_servico_id,
            })
            url = f"{TRANSP_API_URL}/order_events_types/list?{query}"
            client = RequestClient(
                method="GET",
                url=url,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            response_travel = client.send_api_request()

            if isinstance(response_travel, list):
                travel_event_types = [
                    ev for ev in response_travel
                    if str(ev.get("active")).lower() == "true"
                ]
                if not travel_event_types:
                    messages.warning(
                        request,
                        f"Nenhum tipo de evento encontrado para cliente "
                        f"'{cliente_nome}' e tipo '{order_type_api}'.",
                    )
            elif isinstance(response_travel, dict) and response_travel.get("detail"):
                messages.error(request, response_travel.get("detail"))
            else:
                messages.warning(
                    request, "A API não retornou eventos em formato esperado."
                )
        except Exception as e:
            messages.error(request, f"Erro ao consultar eventos: {e}")
    else:
        messages.warning(
            request,
            f"Selecione cliente e tipo de serviço válidos. "
            f"Cliente='{cliente_nome}' | Tipo='{tipo_servico_id}'",
        )

    request.session["lista_viagens_modal_eventos"] = {
        "selected_travel_ids": selected_travel_ids,
        "travel_event_types": travel_event_types,
        "cliente": client_id,
        "tipo_servico": tipo_servico_id,
    }
    return redirect("transportes:lista_viagens")


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def lista_viagens_atrelar_motorista(request):
    from transportes.utils.atribuir_motorista import (
        montar_url_atualizar_motorista,
        obter_contexto_atribuir_motorista,
        validar_pa_atribuir_motorista,
    )

    if request.method != "POST":
        return redirect("transportes:lista_viagens")

    selected_travel_ids = request.POST.getlist("travels_selecionadas")
    carrier_id = (request.POST.get("carrier_id") or "").strip()
    motorista_id = (request.POST.get("motorista_id") or "").strip()
    motorista_nome = (request.POST.get("motorista_nome") or "").strip()
    pa_id = request.POST.get("pa_selecionada")
    created_by = request.user.username
    ctx_atribuir = obter_contexto_atribuir_motorista(request.user)

    if not selected_travel_ids:
        messages.error(request, "Selecione pelo menos uma viagem.")
        return redirect("transportes:lista_viagens")

    ok_pa, erro_pa, pa_id = validar_pa_atribuir_motorista(request.user, pa_id)
    if not ok_pa:
        messages.error(request, erro_pa)
        return redirect("transportes:lista_viagens")

    if not ctx_atribuir["pode_escolher_transportadora"]:
        carrier_id = ""

    if not motorista_id:
        messages.error(request, "Selecione um motorista válido.")
        return redirect("transportes:lista_viagens")

    try:
        ids_limpos = [
            int(str(travel_id).strip())
            for travel_id in selected_travel_ids
            if str(travel_id).strip()
        ]
        if not ids_limpos:
            messages.error(request, "Nenhuma viagem válida foi selecionada.")
            return redirect("transportes:lista_viagens")

        update_driver_payload = [{
            "travels_ids": ids_limpos,
            "driver_id": int(motorista_id),
        }]
        update_driver_url = montar_url_atualizar_motorista(created_by, carrier_id)
        update_driver_client = RequestClient(
            method="POST",
            url=update_driver_url,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            request_data=update_driver_payload,
        )
        update_driver_response = update_driver_client.send_api_request()

        if isinstance(update_driver_response, dict) and update_driver_response.get("detail"):
            detail = update_driver_response.get("detail")
            if isinstance(detail, list):
                detail = " | ".join(str(item) for item in detail)
            messages.error(request, f"Erro ao atrelar motorista: {detail}")
        else:
            messages.success(
                request,
                f"Motorista {motorista_nome or motorista_id} vinculado com sucesso "
                f"às viagens selecionadas.",
            )
        return redirect("transportes:lista_viagens")
    except Exception as e:
        messages.error(request, f"Erro ao atrelar motorista: {e}")
        return redirect("transportes:lista_viagens")


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def lista_viagens_criar_evento_lote(request):
    if request.method != "POST":
        return redirect("transportes:lista_viagens")

    selected_travel_ids = request.POST.getlist("travels_selecionadas")

    try:
        event_type_id = int(request.POST.get("event_type_id"))
    except (TypeError, ValueError):
        messages.error(request, "Selecione um tipo de evento.")
        return redirect("transportes:lista_viagens")

    description = (request.POST.get("description") or "").strip()
    created_by = request.user.username
    location_lat = (request.POST.get("location_lat") or "").strip()
    location_long = (request.POST.get("location_long") or "").strip()
    shipping_date_input = (request.POST.get("shipping_date") or "").strip()

    if not shipping_date_input:
        messages.error(request, "Informe a data de envio.")
        return redirect("transportes:lista_viagens")

    shipping_date = parse_datetime(shipping_date_input)
    if shipping_date is None:
        messages.error(request, "Data de envio inválida.")
        return redirect("transportes:lista_viagens")

    if timezone.is_naive(shipping_date):
        shipping_date = timezone.make_aware(
            shipping_date, timezone.get_current_timezone()
        )

    payload_event = {
        "event_type_id": event_type_id,
        "created_by": created_by,
        "shipping_date": shipping_date.isoformat(),
    }
    if description:
        payload_event["description"] = description
    if location_lat:
        payload_event["location_lat"] = location_lat
    if location_long:
        payload_event["location_long"] = location_long

    try:
        ids_limpos = [str(i).strip() for i in selected_travel_ids if str(i).strip()]
        query_ids = "&".join([f"ids={i}" for i in ids_limpos])
        url = f"{TRANSP_API_URL}/v2/order_tracking/create?destination=travel&{query_ids}"

        client = RequestClient(
            method="POST",
            url=url,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            request_data=payload_event,
        )
        response_event = client.send_api_request()

        if isinstance(response_event, dict) and "detail" in response_event:
            messages.error(request, response_event["detail"])
        else:
            request.session.pop("lista_viagens_modal_eventos", None)
            messages.success(request, "Eventos criados com sucesso!")
            return redirect("transportes:lista_viagens")
    except Exception as e:
        messages.error(request, f"Erro ao criar evento: {e}")

    return redirect("transportes:lista_viagens")
