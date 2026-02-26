from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
import math
from ...forms import ConsultaOStranspForm
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def consulta_os_transp(request):
    titulo = "Consulta OS"
    resultado_api = []

    url_status = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_status,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp["detail"])
        resp = []

    form = ConsultaOStranspForm(request.GET or None, payload=resp)
    if request.method == "POST":
        data = request.POST.copy()
        data.pop("csrfmiddlewaretoken", None)
        for k in list(data.keys()):
            if data.get(k) in (None, "", "None"):
                data.pop(k, None)
        return redirect(f"{request.path}?{data.urlencode()}")

    data = request.GET

    try:
        page = int(data.get("page", 1))
    except ValueError:
        page = 1
    page = max(page, 1)

    limit = 20
    offset = (page - 1) * limit

    qs = data.copy()
    qs.pop("page", None)
    base_qs = qs.urlencode()

    should_query = (
        data.get("enviar_evento") == "1"
        or (
            data.get("page") and data.get("enviar_evento") == "1"
        )
    )

    total = 0
    total_pages = 1
    pages = [page]
    has_prev = page > 1
    has_next = False

    if should_query:
        params = {}

        tipo_os = (data.get("tipo_os") or "").strip().upper()
        numero_os = (data.get("numero_os") or "").strip()

        if numero_os and not tipo_os:
            messages.error(
                request, "Selecione o tipo da OS (IN/EX) para pesquisar pelo número.")
            numero_os = ""
        elif tipo_os and not numero_os:
            messages.error(request, "Informe o número da OS para pesquisar.")
            tipo_os = ""

        if numero_os:
            if tipo_os == "IN":
                params["IN"] = numero_os
            elif tipo_os == "EX":
                params["EX"] = numero_os
            else:
                messages.error(request, "Tipo de OS inválido. Use IN ou EX.")
                params.pop("IN", None)
                params.pop("EX", None)

        cliente_id = (data.get("client") or "").strip()
        if cliente_id:
            cliente_obj = next((c for c in resp if str(
                c.get("id")) == str(cliente_id)), None)
            if cliente_obj and cliente_obj.get("nome"):
                params["cliente"] = cliente_obj["nome"]

        status_id = (data.get("status") or "").strip()
        if status_id:
            params["status_id"] = status_id

        order_type = (data.get("order_type") or "").strip()
        if order_type:
            params["order_type"] = order_type

        params["limit"] = limit
        params["offset"] = offset

        url_lista = f"{TRANSP_API_URL}/service_orders/list"
        lista_request = RequestClient(
            method="get",
            url=url_lista,
            headers={"accept": "application/json"},
            request_data=params,
        )
        resultado_api = lista_request.send_api_request()

        if isinstance(resultado_api, dict) and resultado_api.get("detail"):
            messages.error(request, resultado_api["detail"])
            resultado_api = []
        else:
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
                resultado_api = items if isinstance(items, list) else []

            elif isinstance(resultado_api, list):
                total = 0

            else:
                resultado_api = []
                total = 0

            if total:
                total_pages = max(1, math.ceil(total / limit))
                has_next = page < total_pages
            else:
                has_next = len(resultado_api) == limit
                total_pages = page + (1 if has_next else 0)

            start = max(1, page - 2)
            end = min(total_pages, page + 2)
            pages = list(range(start, end + 1))

    return render(
        request,
        "transportes/transportes/consulta_os_transp.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "orders": resultado_api if isinstance(resultado_api, list) else [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": has_next,
                "prev_page": page - 1,
                "next_page": page + 1,
                "pages": pages,
                "base_qs": base_qs,
            },
        },
    )
