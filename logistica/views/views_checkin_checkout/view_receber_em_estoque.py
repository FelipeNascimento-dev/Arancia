from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from ...forms import ReceberEmEstoqueForm
from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient


JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def receber_em_estoque(request):
    titulo = "Receber em Estoque"

    form = ReceberEmEstoqueForm(
        request.POST or None,
        nome_form=titulo
    )

    numero_romaneio = None
    result = None
    itens_romaneio = []

    if request.method == "POST":
        numero_romaneio = request.POST.get("numero_romaneio")

        if numero_romaneio:
            try:
                url = f"{STOCK_API_URL}/v2/romaneios/read_for_receive/{numero_romaneio}"
                client = RequestClient(
                    url=url,
                    method="GET",
                    headers={
                        "Accept": JSON_CT,
                        "Content-Type": JSON_CT,
                    },
                )
                result = client.send_api_request()

                if 'detail' in result:
                    messages.error(request, result.get('detail'))
                else:
                    messages.success(
                        request, f"Romaneio {numero_romaneio} encontrado com sucesso!")
                    itens_romaneio = result.get("items", [])

            except Exception as e:
                messages.error(request, "Erro ao consultar o romaneio.")

        else:
            messages.error(request, "Informe o número do romaneio.")

    return render(
        request,
        'logistica/templates_checkin_checkout/receber_em_estoque.html',
        {
            'form': form,
            'site_title': titulo,
            'botao_texto': 'Consultar Romaneio',
            'romaneio_data': result,
            'itens_romaneio': itens_romaneio,
            'numero_romaneio': numero_romaneio,
        }
    )
