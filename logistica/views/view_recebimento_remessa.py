from django.contrib import messages
from django.shortcuts import render
import json
import logging

from utils.request import RequestClient
from ..forms import RecebimentoRemessaForm

logger = logging.getLogger(__name__)

API_URL = "http://192.168.0.214/IntegrationXmlAPI/api/v2/centros_e_deps/O"


def _fetch_api_rows():
    client = RequestClient(url=API_URL, method="GET", headers={
                           "Accept": "application/json"})
    resp = client.send_api_request_no_json(stream=False)

    try:
        data = resp.json()
    except Exception as e:
        logger.exception("Falha ao desserializar JSON da API: %s", e)
        data = []

    if isinstance(data, dict):
        for key in ("results", "data", "items", "centros", "centros_e_deps"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return []
    return data if isinstance(data, list) else []


def _build_choices_and_map(rows):

    centers = []
    all_deps = set()
    depositos_by_centro = {}

    for item in rows or []:
        c_value = (
            item.get("centro_code")
            or item.get("center_code")
            or item.get("codigo")
            or item.get("code")
            or item.get("id")
            or item.get("centro")
            or ""
        )
        c_label = (
            item.get("centro_name")
            or item.get("center_name")
            or item.get("descricao")
            or item.get("nome")
            or item.get("name")
            or str(c_value)
        )

        if not c_value:
            continue

        c_value = str(c_value)
        c_label = str(c_label)

        centers.append((c_value, c_label))

        deps = (
            item.get("depositos")
            or item.get("warehouses")
            or item.get("deps")
            or item.get("itens")
            or []
        )
        dep_list = []
        for d in deps or []:
            d_value = (
                d.get("code")
                or d.get("codigo")
                or d.get("id")
                or d.get("dep_code")
                or ""
            )
            d_label = (
                d.get("name")
                or d.get("nome")
                or d.get("descricao")
                or str(d_value)
            )
            if not d_value:
                continue
            d_tuple = (str(d_value), str(d_label))
            dep_list.append(d_tuple)
            all_deps.add(d_tuple)

        depositos_by_centro[c_value] = dep_list

    def _dedup(seq):
        seen = set()
        out = []
        for t in seq:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out

    distribution_center_choices = _dedup(centers)
    ware_house_code_choices = _dedup(list(all_deps))

    distribution_center_choices.sort(key=lambda x: x[1])
    ware_house_code_choices.sort(key=lambda x: x[1])
    for k in list(depositos_by_centro.keys()):
        depositos_by_centro[k] = sorted(
            _dedup(depositos_by_centro[k]), key=lambda x: x[1])

    logger.info(
        "Carregados %d centros e %d depósitos (únicos).",
        len(distribution_center_choices), len(ware_house_code_choices)
    )

    return distribution_center_choices, ware_house_code_choices, depositos_by_centro


def recebimento_remessa(request):
    titulo = 'Recebimento por Remessa'
    try:
        rows = _fetch_api_rows()
    except Exception as e:
        rows = []
        messages.error(request, f"Falha ao carregar centros/depósitos: {e}")

    dc_choices, wh_choices, depositos_by_centro = _build_choices_and_map(rows)

    if not dc_choices:
        messages.warning(request, "Nenhum centro retornado pela API.")
    if not wh_choices:
        pass

    if request.method == "POST":
        form = RecebimentoRemessaForm(
            request.POST,
            nome_form=titulo,
            distribution_center_choices=dc_choices,
            ware_house_code_choices=wh_choices,
        )
        if form.is_valid():
            messages.success(request, "Consulta realizada com sucesso.")
    else:
        form = RecebimentoRemessaForm(
            nome_form=titulo,
            distribution_center_choices=dc_choices,
            ware_house_code_choices=wh_choices,
        )

    return render(
        request,
        "logistica/recebimento_remessa.html",
        {
            "form": form,
            "botao_texto": "Consultar",
            "depositos_map_json": json.dumps(depositos_by_centro),
        },
    )
