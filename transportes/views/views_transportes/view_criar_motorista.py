from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import TRANSP_API_URL, API_BASE, TOKEN
from utils.request import RequestClient
from django.contrib import messages


@login_required(login_url='logistica:login')
@permission_required("logistica.gestao_total", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def driver_ger(request):
    if request.method == "POST":

        data = {
            "username": request.POST.get("username"),
            "pwd": request.POST.get("pwd"),
            "pwd_confirm": request.POST.get("pwd"),
            "name": request.POST.get("name"),
            "phone": request.POST.get("phone"),
            "email": request.POST.get("email"),
            "cod_base": 'CTBSEQ',
            "nome_unidade": request.POST.get("nome_unidade"),
            "documento": request.POST.get("document"),
            "profile": "driver",
            "user_created_id": request.user.id,
            "gai_id": int(request.POST.get("gai_id")),
        }

        print(data)

        url = f"{API_BASE}/v1/auth/create/"

        client = RequestClient(
            method="POST",
            url=url,
            request_data=data,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
                "access_token": TOKEN,
            },
        )

        response = client.send_api_request()

        if 'detail' in response:
            messages.error(request, response.get('detail'))
        else:
            messages.success(request, "Motorista criado com sucesso!")

    search = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))

    limit = 10
    offset = (page - 1) * limit

    params = {
        "limit": limit,
        "offset": offset,
    }

    if search:
        params["Nome"] = search

    url = f"{TRANSP_API_URL}/Carriers/driver/list"

    client = RequestClient(
        method="GET",
        url=url,
        request_data=params,
        headers={"accept": "application/json"},
    )

    resp = client.send_api_request()

    drivers = resp if isinstance(resp, list) else []

    url_carrier = f"{TRANSP_API_URL}/Carriers/list"

    client_carrier = RequestClient(
        method="GET",
        url=url_carrier,
        request_data={},
        headers={"accept": "application/json"},
    )

    resp_carrier = client_carrier.send_api_request()

    carriers = resp_carrier if isinstance(resp_carrier, list) else []

    has_next = len(drivers) == limit
    has_prev = page > 1

    return render(
        request,
        "transportes/transportes/criar_motorista.html",
        {
            "drivers": drivers,
            "carriers": carriers,
            "search": search,
            "page": page,
            "has_next": has_next,
            "has_prev": has_prev,
            "site_title": "Gerenciamento de Motoristas",
            "current_parent_menu": "transportes",
            "current_menu": "driver_ger",
        },
    )
