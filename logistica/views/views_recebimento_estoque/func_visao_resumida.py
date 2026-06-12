import json
from urllib.parse import urlencode
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def _top_entries(data_map, limit=12):
    ordenado = sorted(
        data_map.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    if len(ordenado) <= limit:
        return ordenado
    top = ordenado[:limit]
    restante = sum(valor for _, valor in ordenado[limit:])
    if restante:
        top.append(("Outros", restante))
    return top


def build_resumo_chart_data(resumo):
    por_pa = {}
    por_produto = {}
    por_tipo = {}
    por_ztipo = {}

    for pa_item in resumo or []:
        pa_nome = pa_item.get("pa") or "Sem PA"
        for st in pa_item.get("stock_types") or []:
            total = st.get("total") or 0
            tipo = st.get("type") or "Sem tipo"

            por_pa[pa_nome] = por_pa.get(pa_nome, 0) + total
            por_tipo[tipo] = por_tipo.get(tipo, 0) + total

            for produto, qtd in (st.get("qtd_por_produto") or {}).items():
                por_produto[produto] = por_produto.get(produto, 0) + (qtd or 0)

            for ztipo, qtd in (st.get("qtd_por_ztipo") or {}).items():
                por_ztipo[ztipo] = por_ztipo.get(ztipo, 0) + (qtd or 0)

    def _serialize(data_map, limit=12):
        entries = _top_entries(data_map, limit=limit)
        return {
            "labels": [label for label, _ in entries],
            "values": [valor for _, valor in entries],
        }

    return {
        "por_pa": _serialize(por_pa, limit=10),
        "por_produto": _serialize(por_produto, limit=12),
        "por_tipo": _serialize(por_tipo, limit=8),
        "por_ztipo": _serialize(por_ztipo, limit=12),
    }


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

    chart_data = build_resumo_chart_data(resumo)

    return resumo, totais, produtos_unicos, chart_data
