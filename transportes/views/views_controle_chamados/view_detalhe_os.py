from django.shortcuts import render
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib import messages

TOKEN = "123"


def detalhe_os(request, os):
    os_number = os

    url = f"{API_BASE}/v3/controle_campo/chamados/detalhes_os/{os_number}"
    headers = {
        "accept": "application/json",
        "access_token": TOKEN,
        "Content-Type": "application/json",
    }

    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
    )

    resp = client.send_api_request()

    if not resp or 'detail' in resp:
        messages.error(
            request,
            resp.get("detail", "Chamado não encontrado!")
        )
        return render(
            request,
            'transportes/controle_chamados/detalhe_os.html',
            {'os_detail': None}
        )

    messages.success(request, "OS encontrada!")

    return render(
        request,
        'transportes/controle_chamados/detalhe_os.html',
        {
            'os_detail': resp,
            "site_title": 'Detalhes da OS',
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_campo",
            "current_submenu": "controle_chamados",
            "current_subsubmenu": "consulta_os",
        },
    )
