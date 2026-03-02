from django.shortcuts import render
from ...forms import ListaViagensForm
from django.contrib import messages
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required


def lista_viagens(request):
    titulo = "Lista de Viagens"

    url_cliente = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_cliente,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp["detail"])
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
        messages.error(request, resp_transportadora["detail"])
        resp_transportadora = []

    if request.method == "POST":
        form = ListaViagensForm(request.POST, nome_form=titulo,
                                clientes=resp, transportadoras=resp_transportadora)
    else:
        form = ListaViagensForm(
            nome_form=titulo, clientes=resp, transportadoras=resp_transportadora)

    return render(request, 'transportes/transportes/lista_viagens.html', {
        "botao_texto": 'Consultar',
        "site_title": titulo,
        "form": form,
        "transportadoras": resp_transportadora,
    })
    1
