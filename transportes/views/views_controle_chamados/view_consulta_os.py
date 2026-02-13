from django.shortcuts import render, redirect
from ...forms import ConsultaOSForm
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib import messages

TOKEN = "123"


def consulta_os(request):
    titulo = 'Consulta de OS'
    form = ConsultaOSForm(request.POST, nome_form=titulo)

    if request.method == 'POST' and 'enviar_evento':
        numero_os = request.POST.get("ordem_servico")
        os = numero_os

        if not numero_os:
            messages.error(request, "Digite um numero de OS")
        else:
            url = f"{API_BASE}/v3/controle_campo/chamados/detalhes_os/{numero_os}"
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

            print(resp)

            if 'detail' in resp:
                messages.error(request, resp.get(
                    "detail", "Chamado não encontrado!"))
            else:
                return redirect('transportes:detalhe_os', os=os)

    form.errors.pop("ordem_servico", None)

    return render(
        request,
        'transportes/controle_chamados/consulta_os.html', {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_campo",
            "current_submenu": "controle_chamados",
            "current_subsubmenu": "consulta_os",
        },
    )
