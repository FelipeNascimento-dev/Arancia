from django.contrib import messages
from django.shortcuts import render
import json
from collections import defaultdict
from utils.request import RequestClient
from ..forms import RecebimentoRemessaForm


API_URL = "http://192.168.0.214/IntegrationXmlAPI/api/v2/centros_e_deps/O"


def _fetch_api_rows():
    client = RequestClient(url=API_URL, method="GET", headers={
                           "Accept": "application/json"})
    resp = client.send_api_request_no_json(stream=False)
    data = resp.json() if hasattr(resp, "json") else []
    return data if isinstance(data, list) else []


def _build_choices(rows):
    centro_label = {}
    depositos_map = defaultdict(set)
    for r in rows:
        cod_c = (r.get("cod_centro") or "").strip()
        nome_c = (r.get("nome_centro") or "").strip()
        cod_d = (r.get("cod_deposito") or "").strip()
        nome_d = (r.get("nome_deposito") or "").strip()
        if not cod_c:
            continue
        if cod_c not in centro_label:
            centro_label[cod_c] = f"{cod_c} — {nome_c}" if nome_c else cod_c
        if cod_d:
            label = f"{cod_d} — {nome_d}" if nome_d else cod_d
            depositos_map[cod_c].add((cod_d, label))
    centro_choices = sorted(centro_label.items(), key=lambda kv: kv[1])
    depositos_by_centro = {
        k: sorted(list(v), key=lambda t: t[1]) for k, v in depositos_map.items()}
    return centro_choices, depositos_by_centro


def recebimento_remessa(request):
    titulo = 'Recebimento por Remessa'

    try:
        rows = _fetch_api_rows()
    except Exception as e:
        rows = []
        messages.error(request, f"Falha ao carregar centros/depósitos: {e}")

    centro_choices, depositos_by_centro = _build_choices(rows)

    if request.method == "POST":
        form = RecebimentoRemessaForm(
            request.POST,
            nome_form=titulo,
            distribution_center_choices=centro_choices,
            depositos_by_centro=depositos_by_centro,
        )
        if form.is_valid():
            messages.success(request, "Consulta realizada com sucesso.")
    else:
        form = RecebimentoRemessaForm(
            nome_form=titulo,
            distribution_center_choices=centro_choices,
            depositos_by_centro=depositos_by_centro,
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
