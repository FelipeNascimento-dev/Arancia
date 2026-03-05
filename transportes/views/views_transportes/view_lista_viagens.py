from django.shortcuts import render, redirect
from ...forms import ListaViagensForm
from django.contrib import messages
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from datetime import datetime


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.transportes', raise_exception=True)
def lista_viagens(request):
    titulo = "Lista de Viagens"
    travels = []

    url_cliente = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_cliente,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()
    if isinstance(resp, dict) and resp.get("detail"):
        resp = []

    url_transportadora = f"{TRANSP_API_URL}/Carriers/list"
    client = RequestClient(
        method="get",
        url=url_transportadora,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp_transportadora = client.send_api_request()
    if isinstance(resp_transportadora, dict) and resp_transportadora.get("detail"):
        resp_transportadora = []

    if request.method == "POST" and "enviar_evento" in request.POST:
        cliente = request.POST.get("cliente")
        transportadora = request.POST.get("transportadora")

        request.session["filtro_viagem"] = {
            "cliente": cliente,
            "transportadora": transportadora
        }

    filtros = request.session.get("filtro_viagem", {})

    cliente = filtros.get("cliente")
    transportadora = filtros.get("transportadora")

    form = ListaViagensForm(
        initial={
            "cliente": cliente,
            "transportadora": transportadora
        },
        nome_form=titulo,
        clientes=resp,
        transportadoras=resp_transportadora
    )

    if cliente or transportadora:
        try:
            url_travel = f"{TRANSP_API_URL}/order_travels/list/general?cliente={cliente}&transportadora={transportadora}"
            client = RequestClient(
                method="get",
                url=url_travel,
                headers={"accept": "application/json",
                         "Content-Type": "application/json"},
            )
            resp_travel = client.send_api_request()

            if isinstance(resp_travel, list):
                travels = resp_travel

                for t in travels:
                    end_date = t.get("travel", {}).get("end_date")

                    if end_date and end_date != "None":
                        try:
                            dt = datetime.fromisoformat(
                                end_date.replace("Z", "+00:00"))
                            t["travel"]["end_date_formatada"] = dt.strftime(
                                "%d/%m/%Y %H:%M")
                        except Exception:
                            t["travel"]["end_date_formatada"] = end_date
                    else:
                        t["travel"]["end_date_formatada"] = None

        except Exception:
            travels = []

    paginator = Paginator(travels, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'transportes/transportes/lista_viagens.html', {
        "botao_texto": 'Consultar',
        "current_parent_menu": "transportes",
        "current_menu": "lista_viagens",
        "site_title": titulo,
        "form": form,
        "travels": page_obj,
    })
