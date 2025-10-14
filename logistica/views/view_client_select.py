from ..forms import ClientSelectForm
from django.shortcuts import render, redirect
from django.contrib import messages
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from django.contrib.auth.decorators import login_required, permission_required


JSON_CT = "application/json"


@login_required(login_url='logistica:login')
def client_select(request):
    titulo = "Seleção de Cliente"

    form = ClientSelectForm(request.POST, nome_form=titulo)

    if request.method == 'POST':
        form = ClientSelectForm(request.POST, nome_form=titulo)

        if form.is_valid():
            url: f"{STOCK_API_URL}/v1/clients/"
            client = RequestClient(
                url=url,
                method="GET",
                headers={"Accept": JSON_CT},
            )
        else:
            messages.error(request, "Falha ao importar os clientes.")
    else:
        form = ClientSelectForm(nome_form=titulo)
    return render(request, 'logistica/client_select.html', {
        'form': form,
        'site_title': titulo,
        'botao_texto': 'Consultar Cliente'
    })
