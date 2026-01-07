import json
from collections import Counter
from urllib.parse import urlencode
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def func_visao_detalhada(request, form, sales_channels_map):

    client = form.cleaned_data["client"]
    pa_ids = [int(i) for i in form.cleaned_data["cd_estoque"]]

    status = request.POST.get("status", "IN_DEPOT")
    limit = int(request.POST.get("limit", 25))
    offset = int(request.POST.get("offset", 0))

    stock_type = request.POST.get("stock_type")
    if stock_type:
        stock_type = stock_type.strip()

    query_params = [
        ("status", status),
        ("offset", offset),
        ("limit", limit),
    ]

    if stock_type:
        query_params.append(("stock_type", stock_type))

    for pa in pa_ids:
        query_params.append(("locations_ids", pa))

    qs = urlencode(query_params, doseq=True)
    url = f"{STOCK_API_URL}/v1/items/list-byid/{client}?{qs}"

    resultado = RequestClient(
        url=url,
        method="GET",
        headers={"Accept": JSON_CT}
    ).send_api_request()

    if isinstance(resultado, str):
        try:
            resultado = json.loads(resultado)
        except:
            resultado = []

    itens = resultado if isinstance(resultado, list) else []

    stock_type = request.POST.get("stock_type")

    if stock_type:
        stock_type = stock_type.strip()

        itens = [
            i for i in itens
            if i.get("stock_type", "").strip() == stock_type
        ]

    has_more = len(itens) == limit
    page_number = (offset // limit) + 1
    total_pages = page_number + 1 if has_more else page_number

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

    TZ_UTC = ZoneInfo("UTC")
    TZ_BR = ZoneInfo("America/Sao_Paulo")

    def parse_dt(dt):
        if not dt:
            return None

        try:
            dt_utc = datetime.fromisoformat(
                dt.replace("Z", "+00:00")
            ).astimezone(TZ_UTC)

            return dt_utc.astimezone(TZ_BR)

        except Exception:
            return None

    for item in itens:
        dt = parse_dt(item.get("last_movement_in_date"))

        if not dt or dt == datetime.min:
            item["dias_no_estoque"] = None
            continue

        hoje = date.today()
        data_mov = dt.date()

        dias = (hoje - data_mov).days + 1

        item["dias_no_estoque"] = max(dias, 1)
        item["last_movement_in_date"] = dt.strftime("%d/%m/%Y %H:%M:%S")

    itens = sorted(
        itens,
        key=lambda x: parse_dt(x.get("last_movement_in_date")) or datetime.min,
        reverse=False
    )

    agora = datetime.now()
    limite = agora - timedelta(days=30)

    for i in itens:
        try:
            dt = datetime.fromisoformat(
                i.get("last_movement_in_date", "").replace("Z", ""))
        except:
            dt = None
        i["alerta"] = (dt is not None and dt < limite)

    url_produtos = f"{STOCK_API_URL}/v1/products/{client}"

    produtos_api = RequestClient(
        url=url_produtos,
        method="GET",
        headers={"Accept": JSON_CT}
    ).send_api_request()

    if isinstance(produtos_api, str):
        try:
            produtos_api = json.loads(produtos_api)
        except:
            produtos_api = []

    return (
        itens,
        totais,
        produtos_unicos,
        limit,
        offset,
        has_more,
        total_pages,
        page_number,
        produtos_api,
    )
