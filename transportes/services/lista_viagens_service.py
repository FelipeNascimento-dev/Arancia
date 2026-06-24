"""Regras de consulta, paginação e enrich da Lista de Viagens."""

from __future__ import annotations

import json
import math
from datetime import datetime
from urllib.parse import urlencode

from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient

from transportes.services.transportes_metadata_service import (
    FILTRO_CAMPOS_LISTA_VIAGENS,
)
from transportes.utils.baseline import _payload_metrics

PAGE_SIZE = 50
SESSION_KEY_LISTA_VIAGENS_FILTROS = "lista_viagens_filtros"
LIST_API_TIMEOUT = 30


def formatar_data(data_str, com_hora=True):
    if not data_str or data_str == "None":
        return None
    try:
        dt = datetime.fromisoformat(str(data_str).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")
    except Exception:
        return data_str


def filtros_para_querystring(filtros, filtro_campos=None, extra=None):
    filtro_campos = filtro_campos or FILTRO_CAMPOS_LISTA_VIAGENS
    skip = {"offset", "limit", "designation_id", "driver_nome", "status_id"}
    params = dict(extra or {})
    for campo in filtro_campos:
        if campo in skip:
            continue
        valor = filtros.get(campo)
        if valor in [None, "", [], ()]:
            continue
        params[campo] = valor
    return urlencode(params, doseq=True)


def montar_filtros_lista_viagens(post_data, filtro_campos=None):
    filtro_campos = filtro_campos or FILTRO_CAMPOS_LISTA_VIAGENS
    filtros = {}
    campos_multiplos = {"tipo_servico", "status_list"}
    for campo in filtro_campos:
        if campo in campos_multiplos:
            valor = post_data.getlist(campo)
            valor = [v.strip() for v in valor if str(v).strip()]
        else:
            valor = post_data.get(campo, "")
            if isinstance(valor, str):
                valor = valor.strip()
        filtros[campo] = valor
    return filtros


def build_api_params(filtros, offset, limit, tipo_api_map, status_api_map):
    params = {}
    for campo in FILTRO_CAMPOS_LISTA_VIAGENS:
        valor = filtros.get(campo)
        if campo == "Response":
            params["Response"] = valor or "resume"
            continue
        if valor in [None, "", [], ()]:
            continue
        if campo in [
            "designation_id",
            "driver_nome",
            "created_at",
            "offset",
            "limit",
            "status_id",
        ]:
            continue
        if campo == "pa_selecionada":
            params["designation_id"] = valor
        elif campo == "tipo_servico":
            tipos_api = []
            for item in valor:
                mapped = tipo_api_map.get(str(item), item)
                if mapped and mapped not in tipos_api:
                    tipos_api.append(mapped)
            if tipos_api:
                params["order_type"] = ",".join(tipos_api)
        elif campo == "status_list":
            status_api = []
            for item in valor:
                mapped = status_api_map.get(str(item), item)
                if mapped and mapped not in status_api:
                    status_api.append(mapped)
            if status_api:
                params["status"] = ",".join(status_api)
        elif campo == "atrasado":
            params["atrasado"] = str(valor).lower()
        elif campo == "os_interna":
            params["IN"] = valor
        elif campo == "os_externa":
            params["EX"] = valor
        else:
            params[campo] = valor

    if "Response" not in params:
        params["Response"] = "resume"
    params["offset"] = offset
    params["limit"] = limit
    return params


def fetch_travels(params, request=None):
    url_travel = (
        f"{TRANSP_API_URL}/v2/order_travel/list/general?"
        f"{urlencode(params, safe=',')}"
    )
    client = RequestClient(
        method="get",
        url=url_travel,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=LIST_API_TIMEOUT,
    )
    resp_travel = client.send_api_request()
    payload_size, _ = _payload_metrics(resp_travel)
    return resp_travel, url_travel, payload_size


def parse_travels_response(resp_travel):
    if isinstance(resp_travel, dict) and resp_travel.get("detail"):
        return [], 0, resp_travel.get("detail")

    if isinstance(resp_travel, dict):
        items = (
            resp_travel.get("items")
            or resp_travel.get("results")
            or resp_travel.get("data")
            or []
        )
        total = (
            resp_travel.get("total")
            or resp_travel.get("count")
            or resp_travel.get("total_count")
            or 0
        )
        return (items if isinstance(items, list) else []), total, None

    if isinstance(resp_travel, list):
        return resp_travel, 0, None

    return [], 0, None


def enrich_travels(travels, include_events=False):
    for t in travels:
        travel_data = t.get("travel", {})
        travel_data["start_date_formatada"] = formatar_data(
            travel_data.get("start_date")
        )
        travel_data["end_date_formatada"] = formatar_data(
            travel_data.get("end_date")
        )
        travel_data["created_at_formatada"] = formatar_data(
            travel_data.get("created_at")
        )
        travel_data["data_limite_entrega_formatada"] = formatar_data(
            travel_data.get("data_limite_entrega")
        )

        eventos = t.get("travel_events", []) or []
        if include_events:
            for ev in eventos:
                ev["created_at_formatada"] = formatar_data(ev.get("created_at"))
                evento_info = ev.get("evento", {}) or {}
                ev["evento_nome"] = evento_info.get("name", "")
                ev["evento_descricao"] = evento_info.get("description", "")
                ev["evento_tipo"] = evento_info.get("type", "")
            eventos.sort(key=lambda x: x.get("created_at") or "")

        t["travel_events"] = eventos
        t["travel_events_count"] = len(eventos)
        if include_events:
            t["travel_events_json"] = json.dumps(
                eventos, ensure_ascii=False, default=str
            )
    return travels


def append_view_mode_to_qs(base_qs: str, view_mode: str) -> str:
    if view_mode != "table":
        return base_qs
    if base_qs:
        if "view_mode=" in base_qs:
            return base_qs
        return f"{base_qs}&view_mode=table"
    return "view_mode=table"


def build_pagination_state(page, total, travels_count):
    has_prev = page > 1
    if total:
        total_pages = max(1, math.ceil(total / PAGE_SIZE))
        has_next = page < total_pages
    else:
        has_next = travels_count == PAGE_SIZE
        total_pages = page + (1 if has_next else 0)
    start = max(1, page - 2)
    end = min(total_pages, page + 2)
    return {
        "page": page,
        "limit": PAGE_SIZE,
        "total": total,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1,
        "next_page": page + 1,
        "pages": list(range(start, end + 1)),
    }


def show_origin_column(travels):
    return any(
        str(
            item.get("service_order", {})
            .get("order_type", {})
            .get("direction", "")
        ).lower()
        == "normal"
        for item in travels
    )


def build_filtros_exibicao(filtros, maps_ctx):
    filtro_campos = FILTRO_CAMPOS_LISTA_VIAGENS
    mapa_campos = {
        "travel_id": "Travel",
        "os_interna": "OS interna",
        "os_externa": "OS externa",
        "cliente": "Cliente",
        "transportadora": "Transportadora",
        "pa_selecionada": "PA",
        "tipo_servico": "Tipo servico",
        "driver_id": "Motorista",
        "driver_nome": "Motorista",
        "status_id": "Status",
        "sem_motorista": "Sem motorista",
        "status_list": "Lista status",
        "cep_origin": "CEP origem",
        "cep_destin": "CEP destino",
        "created_at": "Data criação",
        "data_limite_entrega": "Data limite entrega",
        "designation_id": "Designation",
        "atrasado": "Atrasadas",
        "Response": "Response",
    }
    tipos_map = maps_ctx["tipos_map"]
    status_map = maps_ctx["status_map"]
    clientes_map, transportadoras_map = maps_ctx["clientes_transportadoras_maps"]

    filtros_exibicao = []
    for campo in filtro_campos:
        valor = filtros.get(campo)
        if valor in [None, "", [], ()]:
            continue
        if campo == "driver_id":
            continue

        valor_exibicao = valor
        if campo == "cliente":
            valor_exibicao = clientes_map.get(str(valor), valor)
        elif campo == "transportadora":
            valor_exibicao = transportadoras_map.get(str(valor), valor)
        elif campo == "tipo_servico":
            if isinstance(valor, list):
                valor_exibicao = ", ".join(
                    tipos_map.get(str(v), str(v)) for v in valor
                )
            else:
                valor_exibicao = tipos_map.get(str(valor), valor)
        elif campo == "status_list":
            if isinstance(valor, list):
                valor_exibicao = ", ".join(
                    status_map.get(str(v), str(v)) for v in valor
                )
            else:
                valor_exibicao = status_map.get(str(valor), valor)
        elif campo in ["sem_motorista", "atrasado"]:
            valor_exibicao = (
                "Sim" if str(valor).lower() in ["true", "1", "on"] else "Não"
            )
        elif campo in ["created_at", "data_limite_entrega"]:
            try:
                dt = datetime.strptime(str(valor)[:10], "%Y-%m-%d")
                valor_exibicao = dt.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                valor_exibicao = formatar_data(valor, com_hora=False) or valor
        elif campo == "Response":
            valor_exibicao = (
                "Detalhado" if str(valor).lower() == "detailed" else "Resumido"
            )
        elif isinstance(valor, str):
            valor_exibicao = valor.strip().capitalize()

        filtros_exibicao.append({
            "campo": mapa_campos.get(campo, campo.replace("_", " ").capitalize()),
            "valor": valor_exibicao,
        })
    return filtros_exibicao


def build_extract_params(filtros, tipo_api_map, status_api_map):
    extract_params = {}
    travel_id = filtros.get("travel_id")
    if travel_id not in [None, "", [], ()]:
        extract_params["travel_id"] = travel_id

    os_interna = filtros.get("os_interna")
    if os_interna not in [None, "", [], ()]:
        extract_params["IN"] = os_interna

    os_externa = filtros.get("os_externa")
    if os_externa not in [None, "", [], ()]:
        extract_params["EX"] = os_externa

    for campo, chave in [
        ("cliente", "cliente"),
        ("transportadora", "transportadora"),
    ]:
        valor = filtros.get(campo)
        if valor not in [None, "", [], ()]:
            extract_params[chave] = valor

    pa_selecionada = filtros.get("pa_selecionada")
    if pa_selecionada not in [None, "", [], ()]:
        extract_params["designation_id"] = pa_selecionada

    tipo_servico = filtros.get("tipo_servico")
    if tipo_servico not in [None, "", [], ()]:
        tipos_api = []
        for item in tipo_servico:
            mapped = tipo_api_map.get(str(item), item)
            if mapped and mapped not in tipos_api:
                tipos_api.append(mapped)
        if tipos_api:
            extract_params["tipo_servico"] = ",".join(tipos_api)

    driver_id = filtros.get("driver_id")
    if driver_id not in [None, "", [], ()]:
        extract_params["driver_id"] = driver_id

    sem_motorista = filtros.get("sem_motorista")
    if sem_motorista not in [None, "", [], ()]:
        extract_params["sem_motorista"] = sem_motorista

    atrasado = filtros.get("atrasado")
    if atrasado not in [None, "", [], ()]:
        extract_params["atrasado"] = str(atrasado).lower()

    status_list = filtros.get("status_list")
    if status_list not in [None, "", [], ()]:
        status_api = []
        for item in status_list:
            mapped = status_api_map.get(str(item), item)
            if mapped and mapped not in status_api:
                status_api.append(mapped)
        if status_api:
            extract_params["status_list"] = ",".join(status_api)

    for campo in ["cep_origin", "cep_destin", "data_limite_entrega"]:
        valor = filtros.get(campo)
        if valor not in [None, "", [], ()]:
            extract_params[campo] = valor

    extract_params["Response"] = filtros.get("Response") or "resume"
    return extract_params


def fetch_travel_events(travel_id):
    """Busca eventos de uma viagem (lazy-load do modal)."""
    params = {"Response": "detailed", "travel_id": travel_id, "limit": 1}
    url = (
        f"{TRANSP_API_URL}/v2/order_travel/list/general?"
        f"{urlencode(params, safe=',')}"
    )
    client = RequestClient(
        method="get",
        url=url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=LIST_API_TIMEOUT,
    )
    resp = client.send_api_request()
    travels, _, detail = parse_travels_response(resp)
    if detail:
        return [], detail

    eventos = []
    if travels:
        eventos = travels[0].get("travel_events", []) or []

    for ev in eventos:
        ev["created_at_formatada"] = formatar_data(ev.get("created_at"))
        evento_info = ev.get("evento", {}) or {}
        ev["evento_nome"] = evento_info.get("name", "")
        ev["evento_descricao"] = evento_info.get("description", "")
        ev["evento_tipo"] = evento_info.get("type", "")

    eventos.sort(key=lambda x: x.get("created_at") or "")
    return eventos, None
