import json
from collections import Counter
from urllib.parse import quote

from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def func_visao_detalhada(request, form, sales_channels_map):

    client = form.cleaned_data["client"]
    pa_ids = form.cleaned_data["cd_estoque"]  # lista de PAs
    pa_ids = [int(i) for i in pa_ids]

    status = request.POST.get("status", "IN_DEPOT")

    todos_itens = []

    for pa in pa_ids:

        sales_channel = sales_channels_map.get(pa, "")
        sales_channel_encoded = quote(str(sales_channel), safe='')

        url = (
            f"{STOCK_API_URL}/v1/items/list/{client}"
            f"?status={status}"
            f"&sales_channels%5B%5D={sales_channel_encoded}"
        )

        resultado = RequestClient(url=url, method="GET",
                                  headers={"Accept": JSON_CT}).send_api_request()

        if isinstance(resultado, str):
            try:
                resultado = json.loads(resultado)
            except:
                resultado = {}

        itens = resultado.get("items", []) if isinstance(
            resultado, dict) else resultado
        if not isinstance(itens, list):
            itens = []

        todos_itens.extend(itens)

    totais = {
        "total_geral": len(todos_itens),
        "por_status": Counter(i.get("status") for i in todos_itens),
        "por_produto": Counter(i.get("product_id") for i in todos_itens),
    }

    produtos_unicos = sorted({
        i.get("product_id")
        for i in todos_itens
        if i.get("product_id")
    })

    return todos_itens, totais, produtos_unicos
