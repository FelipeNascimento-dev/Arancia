from django.shortcuts import render
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages
from django.db.models import Q
from logistica.models import Group, GroupAditionalInformation


def detalhe_os_transp(request, order_number):

    url = f"{TRANSP_API_URL}/service_orders/{order_number}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
    )

    resp = client.send_api_request()

    url_carriers = f"{TRANSP_API_URL}/Carriers/list"
    carriers_request = RequestClient(
        method="get",
        url=url_carriers,
        headers=headers
    )
    carriers_resp = carriers_request.send_api_request()

    carriers = []
    if isinstance(carriers_resp, dict):
        carriers = carriers_resp.get(
            "items") or carriers_resp.get("results") or []
    elif isinstance(carriers_resp, list):
        carriers = carriers_resp

    grupos_base = Group.objects.filter(
        Q(name="arancia_PA") |
        Q(name="arancia_CD") |
        Q(name="arancia_CUSTOMER")
    )

    grupos = GroupAditionalInformation.objects.filter(
        group__in=grupos_base
    ).select_related("group").order_by("nome")

    if request.method == "POST":
        if "criar_cotacao" in request.POST:
            service_order_id = request.POST.get("service_order_id")
            carrier_id = request.POST.get("carrier_id")
            origin_id = request.POST.get("origin_id")
            destination_id = request.POST.get("destination_id")
            estimated_deadline = request.POST.get("estimated_deadline")
            created_by = request.user.username

            def to_float(value, field_name):
                if not value:
                    return 0.0
                try:
                    return float(str(value).replace(",", "."))
                except ValueError:
                    messages.error(
                        request, f"Valor inválido para {field_name}.")
                    return 0.0

            total_weight = to_float(
                request.POST.get("total_weight"), "Peso Total")
            total_volume = to_float(request.POST.get(
                "total_volume"), "Volume Total")
            estimated_price = to_float(request.POST.get(
                "estimated_price"), "Valor Estimado")

            try:
                url_quote = f"{TRANSP_API_URL}/quotes/create"
            except:
                pass

    return render(request, 'transportes/transportes/detalhe_os.html', {
        "order_number": order_number,
        "payload": resp,
        "carriers": carriers,
        "grupos": grupos,
    })
