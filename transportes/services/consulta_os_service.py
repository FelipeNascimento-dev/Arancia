"""Regras de consulta e paginação da Lista de OS (transportes)."""

from __future__ import annotations

import math
from datetime import datetime
from urllib.parse import urlencode

from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient

from transportes.utils.baseline import _payload_metrics

PAGE_SIZE = 50
LIST_API_TIMEOUT = 30


def montar_filtros_consulta_os(post_data):
    return {
        "numero_os": (post_data.get("numero_os") or "").strip(),
        "tipo_os": (post_data.get("tipo_os") or "").strip(),
        "client": (post_data.get("client") or "").strip(),
        "pa_selecionada": (post_data.get("pa_selecionada") or "").strip(),
        "origem": (post_data.get("origem") or "").strip(),
        "destino": (post_data.get("destino") or "").strip(),
        "data_inicial": (post_data.get("data_inicial") or "").strip(),
        "data_final": (post_data.get("data_final") or "").strip(),
        "created_at": (post_data.get("created_at") or "").strip(),
        "status": [v.strip() for v in post_data.getlist("status") if v.strip()],
        "order_type": [v.strip() for v in post_data.getlist("order_type") if v.strip()],
        "enviar_evento": "1",
    }


def aplicar_filtro_data(data_source, params):
    created_at = (data_source.get("created_at") or "").strip()
    data_inicial = (data_source.get("data_inicial") or "").strip()
    data_final = (data_source.get("data_final") or "").strip()

    if data_inicial and data_final:
        params["data_inicial"] = data_inicial
        params["data_final"] = data_final
    elif data_inicial:
        params["created_at"] = data_inicial
    elif data_final:
        params["created_at"] = data_final
    elif created_at:
        params["created_at"] = created_at


def add_filtro_exibicao(lista, campo, valor, field, value=None):
    if valor in [None, ""]:
        return
    lista.append({
        "campo": campo,
        "valor": valor,
        "field": field,
        "value": str(value) if value is not None else "",
    })


def build_list_params(data, status_by_id, order_type_by_id, clientes_status):
    params = {}
    filtros_exibicao = []

    aplicar_filtro_data(data, params)

    tipo_os = (data.get("tipo_os") or "").strip().upper()
    numero_os = (data.get("numero_os") or "").strip()

    errors = []
    if numero_os and not tipo_os:
        errors.append(
            "Selecione o tipo da OS (IN/EX) para pesquisar pelo número."
        )
        numero_os = ""
    elif tipo_os and not numero_os:
        errors.append("Informe o número da OS para pesquisar.")
        tipo_os = ""

    if numero_os:
        if tipo_os == "IN":
            params["IN"] = numero_os
        elif tipo_os == "EX":
            params["EX"] = numero_os
        else:
            errors.append("Tipo de OS inválido. Use IN ou EX.")
            params.pop("IN", None)
            params.pop("EX", None)

    cliente_id = (data.get("client") or "").strip()
    if cliente_id:
        cliente_obj = next(
            (c for c in clientes_status if str(c.get("id")) == str(cliente_id)),
            None,
        )
        if cliente_obj and cliente_obj.get("nome"):
            params["cliente"] = cliente_obj["nome"]
            add_filtro_exibicao(
                filtros_exibicao,
                campo="Cliente",
                valor=cliente_obj["nome"],
                field="client",
                value=cliente_id,
            )

    pa_id = (data.get("pa_selecionada") or "").strip()
    if pa_id:
        params["designation_id"] = pa_id
        add_filtro_exibicao(
            filtros_exibicao,
            campo="PA",
            valor=pa_id,
            field="pa_selecionada",
            value=pa_id,
        )

    origem_id = (data.get("origem") or "").strip()
    if origem_id:
        params["origin_id"] = origem_id
        add_filtro_exibicao(
            filtros_exibicao,
            campo="Origem",
            valor=origem_id,
            field="origem",
            value=origem_id,
        )

    destino_id = (data.get("destino") or "").strip()
    if destino_id:
        params["destin_id"] = destino_id
        add_filtro_exibicao(
            filtros_exibicao,
            campo="Destino",
            valor=destino_id,
            field="destino",
            value=destino_id,
        )

    status_ids = [s.strip() for s in data.getlist("status") if s.strip()]
    if status_ids:
        status_textos = []
        for status_id in status_ids:
            status_item = status_by_id.get(status_id)
            if status_item:
                valor = status_item.get("type")
                if valor and valor not in status_textos:
                    status_textos.append(valor)
        if status_textos:
            params["status"] = ",".join(status_textos)
            for status_id in status_ids:
                status_item = status_by_id.get(status_id)
                if status_item:
                    add_filtro_exibicao(
                        filtros_exibicao,
                        campo="Status",
                        valor=status_item.get("type"),
                        field="status",
                        value=status_id,
                    )

    order_type_ids = [ot.strip() for ot in data.getlist("order_type") if ot.strip()]
    if order_type_ids:
        params["order_type"] = ",".join(order_type_ids)
        for order_type_id in order_type_ids:
            order_type_item = order_type_by_id.get(order_type_id)
            if order_type_item:
                add_filtro_exibicao(
                    filtros_exibicao,
                    campo="Tipo de OS",
                    valor=order_type_item.get("type")
                    or str(order_type_item.get("id")),
                    field="order_type",
                    value=order_type_item.get("id"),
                )

    if numero_os:
        add_filtro_exibicao(
            filtros_exibicao,
            campo="Número OS",
            valor=numero_os,
            field="numero_os",
        )
    if tipo_os:
        add_filtro_exibicao(
            filtros_exibicao,
            campo="Tipo",
            valor=tipo_os,
            field="tipo_os",
        )
    if data.get("data_inicial"):
        add_filtro_exibicao(
            filtros_exibicao,
            campo="Data inicial",
            valor=data.get("data_inicial"),
            field="data_inicial",
        )
    if data.get("data_final"):
        add_filtro_exibicao(
            filtros_exibicao,
            campo="Data final",
            valor=data.get("data_final"),
            field="data_final",
        )

    return params, filtros_exibicao, errors


def build_export_params(data, status_by_id, clientes_status):
    extract_params = {}
    aplicar_filtro_data(data, extract_params)

    tipo_os = (data.get("tipo_os") or "").strip().upper()
    numero_os = (data.get("numero_os") or "").strip()

    if numero_os:
        if tipo_os == "IN":
            extract_params["IN"] = numero_os
        elif tipo_os == "EX":
            extract_params["EX"] = numero_os

    cliente_id = (data.get("client") or "").strip()
    if cliente_id:
        cliente_obj = next(
            (c for c in clientes_status if str(c.get("id")) == str(cliente_id)),
            None,
        )
        if cliente_obj and cliente_obj.get("nome"):
            extract_params["cliente"] = cliente_obj["nome"]

    pa_id = (data.get("pa_selecionada") or "").strip()
    if pa_id:
        extract_params["designation_id"] = pa_id

    origem_id = (data.get("origem") or "").strip()
    if origem_id:
        extract_params["origin_id"] = origem_id

    destino_id = (data.get("destino") or "").strip()
    if destino_id:
        extract_params["destin_id"] = destino_id

    status_ids = [s.strip() for s in data.getlist("status") if s.strip()]
    if status_ids:
        status_textos = []
        for status_id in status_ids:
            status_item = status_by_id.get(status_id)
            if status_item:
                valor = status_item.get("type")
                if valor and valor not in status_textos:
                    status_textos.append(valor)
        if status_textos:
            extract_params["status"] = ",".join(status_textos)

    order_type_ids = [ot.strip() for ot in data.getlist("order_type") if ot.strip()]
    if order_type_ids:
        extract_params["order_type"] = ",".join(order_type_ids)

    return extract_params


def fetch_orders(params):
    url_lista = f"{TRANSP_API_URL}/v2/service_order/list"
    lista_request = RequestClient(
        method="get",
        url=url_lista,
        headers={"accept": "application/json"},
        request_data=params,
        timeout=LIST_API_TIMEOUT,
    )
    resultado_api = lista_request.send_api_request()
    payload_size, _ = _payload_metrics(resultado_api)
    return resultado_api, url_lista, payload_size


def parse_orders_response(resultado_api):
    if isinstance(resultado_api, dict) and resultado_api.get("detail"):
        return [], 0, resultado_api.get("detail")

    if isinstance(resultado_api, dict):
        items = (
            resultado_api.get("items")
            or resultado_api.get("results")
            or resultado_api.get("data")
            or []
        )
        total = (
            resultado_api.get("total")
            or resultado_api.get("count")
            or resultado_api.get("total_count")
            or 0
        )
        return (items if isinstance(items, list) else []), total, None

    if isinstance(resultado_api, list):
        return resultado_api, 0, None

    return [], 0, None


def enrich_orders(orders):
    for item in orders:
        created = item.get("created_at")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                item["created_at_fmt"] = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                item["created_at_fmt"] = created
    return orders


def build_pagination_state(page, total, orders_count):
    has_prev = page > 1
    if total:
        total_pages = max(1, math.ceil(total / PAGE_SIZE))
        has_next = page < total_pages
    else:
        has_next = orders_count == PAGE_SIZE
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


def append_view_mode_to_qs(base_qs: str, view_mode: str) -> str:
    if view_mode != "table":
        return base_qs
    if base_qs:
        if "view_mode=" in base_qs:
            return base_qs
        return f"{base_qs}&view_mode=table"
    return "view_mode=table"


def fetch_order_travels(order_number):
    """Viagens de uma OS para lazy-load do modal."""
    url = f"{TRANSP_API_URL}/service_orders/{order_number}"
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
    if isinstance(resp, dict) and resp.get("detail"):
        return [], resp.get("detail")

    travels = resp.get("travels", []) if isinstance(resp, dict) else []
    items = []
    for travel in travels or []:
        status = travel.get("status") or {}
        items.append({
            "id": travel.get("id"),
            "status": status.get("type", "-") if isinstance(status, dict) else "-",
        })
    return items, None
