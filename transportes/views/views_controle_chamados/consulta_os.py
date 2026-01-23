from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from setup.local_settings import API_BASE
from utils.request import RequestClient
from ...forms import ConsultaOSForm

TOKEN = "123"


@csrf_protect
@login_required(login_url='logistica:login')
def consulta_os(request):
    titulo = 'Consulta de OS'

    bases = [
        ("PA_SPO", "São Paulo"),
        ("RJO", "Rio de Janeiro"),
        ("MG", "Minas Gerais"),
    ]

    tecnicos_choices = []

    if request.method == "POST":
        base_selecionada = request.POST.get("base")

        if base_selecionada:
            try:
                url = f"{API_BASE}/v3/controle_campo/tecnicos/{base_selecionada}?offset=0&limit=100"

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

                if isinstance(resp, list):
                    tecnicos_choices = [
                        (tec["username"], tec["name"])
                        for tec in resp
                    ]
                else:
                    messages.error(request, "Nenhum técnico retornado.")

            except Exception as e:
                messages.error(request, f"Erro ao buscar técnicos: {e}")

        form = ConsultaOSForm(request.POST, nome_form=titulo)
        form.fields["base"].choices = bases
        form.fields["tecnico"].choices = tecnicos_choices

        if form.is_valid():
            messages.success(request, "Consulta realizada com sucesso")

    else:
        form = ConsultaOSForm(nome_form=titulo)
        form.fields["base"].choices = bases
        form.fields["tecnico"].choices = []

    return render(
        request,
        'transportes/controle_chamados/consulta_os.html',
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_chamados",
            "current_submenu": "consulta_os",
        },
    )
