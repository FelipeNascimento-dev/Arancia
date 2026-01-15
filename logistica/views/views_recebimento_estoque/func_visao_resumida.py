import json
from urllib.parse import urlencode
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def func_visao_resumida(request, form, sales_channels_map=None):
    client = form.cleaned_data["client"]
    pa_ids = [int(i) for i in form.cleaned_data["cd_estoque"]]

    status = request.POST.get("status", "IN_DEPOT")

    stock_type = request.POST.get("stock_type")
    if stock_type:
        stock_type = stock_type.strip()

    query_params = [
        ("status", status),
    ]

    if stock_type:
        query_params.append(("stock_type", stock_type))

    for pa in pa_ids:
        query_params.append(("locations_ids", pa))

    qs = urlencode(query_params, doseq=True)
    url = f"{STOCK_API_URL}/v1/items/list-byid/{client}/resume?{qs}"

    resultado = RequestClient(
        url=url,
        method="GET",
        headers={"Accept": JSON_CT}
    ).send_api_request()

    if isinstance(resultado, str):
        try:
            resultado = json.loads(resultado)
        except Exception:
            resultado = []

    resumo = resultado if isinstance(resultado, list) else []

    print(resumo)

    total_geral = sum(
        i.get("total", 0) or i.get("quantidade", 0)
        for i in resumo
    )

    totais = {
        "total_geral": total_geral,
        "linhas": len(resumo),
    }

    produtos_unicos = sorted({
        i.get("product_sku")
        for i in resumo
        if i.get("product_sku")
    })

    return resumo, totais, produtos_unicos
