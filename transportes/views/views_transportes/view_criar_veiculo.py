from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import TRANSP_API_URL, API_BASE, TOKEN
from utils.request import RequestClient
from django.contrib import messages


@login_required(login_url='logistica:login')
@permission_required("logistica.gestao_total", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def vehicle_ger(request):
    if request.method == "POST":

        data = {
            "plate": request.POST.get("plate"),
            "manufacturer": request.POST.get("manufacturer"),
            "model": request.POST.get("model"),
            "color": request.POST.get("color"),
            "category": request.POST.get("category"),
            "carrier_id": int(request.POST.get("carrier_id")),
        }

        url = f"{TRANSP_API_URL}/carriers_vehicles/create"

        client = RequestClient(
            method="POST",
            url=url,
            request_data=data,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        response = client.send_api_request()

        if isinstance(response, dict) and "detail" in response:
            messages.error(request, response["detail"])
        else:
            messages.success(request, "Veículo criado")

    url = f"{TRANSP_API_URL}/carriers_vehicles/list"

    client = RequestClient(
        method="GET",
        url=url,
        headers={
            "accept": "application/json",
        },
    )

    resp = client.send_api_request()

    vehicles = resp if isinstance(resp, list) else []

    url_carrier = f"{TRANSP_API_URL}/Carriers/list"

    client_carrier = RequestClient(
        method="GET",
        url=url_carrier,
        headers={"accept": "application/json"},
    )

    resp_carrier = client_carrier.send_api_request()

    carriers = resp_carrier if isinstance(resp_carrier, list) else []

    return render(
        request,
        "transportes/transportes/criar_veiculo.html",
        {
            "vehicles": vehicles,
            "carriers": carriers,
            "site_title": "Gerenciamento de Veículos",
            "current_parent_menu": "transportes",
            "current_menu": "gerenciamento",
            "current_submenu": "vehicle_ger",
        },
    )
