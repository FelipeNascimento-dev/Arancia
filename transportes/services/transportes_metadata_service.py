"""Metadados compartilhados (clientes/status, carriers) e mapas derivados."""

from __future__ import annotations

from transportes.utils.metadata_api import get_transportes_metadata

HARDCODE_PENDING_STATUS = {
    "id": "PENDING",
    "type": "PENDING",
    "description": "PENDING",
}

FILTRO_CAMPOS_LISTA_VIAGENS = [
    "travel_id",
    "os_interna",
    "os_externa",
    "cliente",
    "transportadora",
    "pa_selecionada",
    "tipo_servico",
    "driver_nome",
    "driver_id",
    "status_id",
    "sem_motorista",
    "status_list",
    "cep_origin",
    "cep_destin",
    "offset",
    "limit",
    "created_at",
    "data_limite_entrega",
    "designation_id",
    "atrasado",
    "Response",
]


def fetch_metadata():
    """Clientes/status + carriers em paralelo (cache Django)."""
    return get_transportes_metadata()


def enrich_clientes_status(clientes_status: list) -> list:
    """Aplica status_base e deduplica status por tipo (padrão consulta OS)."""
    if not isinstance(clientes_status, list):
        return []

    for item in clientes_status:
        status_base = item.get("status_base")
        for order_type in item.get("OrderType", []) or []:
            statuses = order_type.get("status", []) or []
            if status_base:
                status_base_type = (status_base.get("type") or "").strip().lower()
                ja_existe = any(
                    (s.get("type") or "").strip().lower() == status_base_type
                    for s in statuses
                )
                if status_base_type and not ja_existe:
                    statuses.append(status_base)

            status_filtrados = []
            vistos = set()
            for st in statuses:
                stype = (st.get("type") or "").strip()
                if not stype:
                    continue
                chave = stype.lower()
                if chave in vistos:
                    continue
                vistos.add(chave)
                status_filtrados.append(st)
            order_type["status"] = status_filtrados
    return clientes_status


def build_status_and_order_type_maps(clientes_status: list) -> tuple[dict, dict]:
    status_by_id = {}
    order_type_by_id = {}
    for cliente in clientes_status:
        for order_type_item in cliente.get("OrderType", []) or []:
            ot_id = str(order_type_item.get("id"))
            order_type_by_id[ot_id] = order_type_item
            for status_item in order_type_item.get("status", []) or []:
                st_id = str(status_item.get("id"))
                status_by_id[st_id] = status_item
    return status_by_id, order_type_by_id


def build_tipos_status_maps(clientes_status: list) -> dict:
    """Mapas para formulário e filtros de exibição (lista viagens)."""
    tipos_por_cliente = {}
    status_por_tipo = {}
    tipos_map = {}
    status_map = {}
    tipo_api_map = {}
    status_api_map = {}

    for cliente in clientes_status:
        cliente_id = str(cliente.get("id"))
        order_types = cliente.get("OrderType", []) or []

        tipos_por_cliente[cliente_id] = [
            {
                "id": str(ot.get("id")),
                "type": ot.get("type", ""),
                "description": ot.get("description", "") or ot.get("type", ""),
            }
            for ot in order_types
        ]

        for ot in order_types:
            tipo_id = str(ot.get("id"))
            tipo_label = ot.get("description") or ot.get("type") or tipo_id
            tipos_map[tipo_id] = tipo_label
            tipo_api_map[tipo_id] = ot.get("type", "")

            statuses_raw = [
                {
                    "id": str(st.get("id")),
                    "type": st.get("type", ""),
                    "description": st.get("description", "") or st.get("type", ""),
                }
                for st in (ot.get("status", []) or [])
            ]

            pending_existe = any(
                str(item.get("type", "")).strip().upper() == "PENDING"
                or str(item.get("id", "")).strip().upper() == "PENDING"
                for item in statuses_raw
            )
            if not pending_existe:
                statuses_raw.insert(0, HARDCODE_PENDING_STATUS.copy())

            status_por_tipo[tipo_id] = statuses_raw

            for st in ot.get("status", []) or []:
                status_id = str(st.get("id"))
                status_label = st.get("type") or st.get("description") or status_id
                status_map[status_id] = status_label
                status_api_map[status_id] = st.get("type", "") or status_id

    return {
        "tipos_por_cliente": tipos_por_cliente,
        "status_por_tipo": status_por_tipo,
        "tipos_map": tipos_map,
        "status_map": status_map,
        "tipo_api_map": tipo_api_map,
        "status_api_map": status_api_map,
    }


def build_clientes_transportadoras_maps(
    clientes_status: list, carriers_list: list
) -> tuple[dict, dict]:
    clientes_map = {
        str(c.get("id")): c.get("nome") or c.get("name") or str(c.get("id"))
        for c in clientes_status
    }
    transportadoras_map = {
        str(t.get("id")): t.get("name") or t.get("nome") or str(t.get("id"))
        for t in carriers_list
    }
    return clientes_map, transportadoras_map


def build_tipos_por_cliente_os(clientes_status: list) -> dict:
    return {
        str(c.get("id")): [
            {"id": str(ot.get("id")), "type": ot.get("type", "")}
            for ot in c.get("OrderType", []) or []
        ]
        for c in clientes_status
    }


def build_status_por_tipo_os(clientes_status: list) -> dict:
    return {
        str(ot.get("id")): [
            {"id": str(st.get("id")), "type": st.get("type", "")}
            for st in (ot.get("status", []) or [])
        ]
        for c in clientes_status
        for ot in c.get("OrderType", []) or []
    }
