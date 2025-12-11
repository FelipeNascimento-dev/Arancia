import json
from collections import Counter
from urllib.parse import urlencode

from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def func_visao_detalhada(request, form, sales_channels_map):

    client = form.cleaned_data["client"]
    pa_ids = form.cleaned_data["cd_estoque"]
    pa_ids = [int(i) for i in pa_ids]

    status = request.POST.get("status", "IN_DEPOT")

    offset = 0
    limit = 50

    query_params = [
        ("status", status),
        ("offset", offset),
        ("limit", limit),
    ]

    for pa in pa_ids:
        query_params.append(("locations_ids", pa))

    qs = urlencode(query_params, doseq=True)

    url = f"{STOCK_API_URL}/v1/items/list-byid/{client}?{qs}"

    resultado = RequestClient(url=url, method="GET",
                              headers={"Accept": JSON_CT}).send_api_request()

    if isinstance(resultado, str):
        try:
            resultado = json.loads(resultado)
        except:
            resultado = []

    itens = resultado if isinstance(resultado, list) else []

    totais = {
        "total_geral": len(itens),
        "por_status": Counter(i.get("status") for i in itens),
        "por_produto": Counter(i.get("product_sku") for i in itens),
    }

    produtos_unicos = sorted({
        i.get("product_sku")
        for i in itens
        if i.get("product_sku")
    })

    return itens, totais, produtos_unicos
