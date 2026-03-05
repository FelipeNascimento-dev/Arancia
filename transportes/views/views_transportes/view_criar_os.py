from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from ...forms import FormCriarOsTransp
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.transportes', raise_exception=True)
def criar_os_transp(request):
    titulo = "Criação de OS"

    url_status = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_status,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp["detail"])
        resp = []

    form = FormCriarOsTransp(request.GET or None,
                             nome_form=titulo, payload=resp)

    if request.method == 'POST':
        if "enviar_evento" in request.POST:
            try:
                payload = {
                    "order_number": request.POST.get("numero_os"),
                    "external_order_number": request.POST.get("ex_order_number"),
                    "created_by": request.user.username,
                    "client_id": request.POST.get("cliente"),
                    "origin_id": request.POST.get("origem"),
                    "destination_id": request.POST.get("destino"),
                    "order_type_id": request.POST.get("tipo_os"),
                    "order_state_id": request.POST.get("status_os"),
                    "extra_information": {},
                }

                url = f"{TRANSP_API_URL}/service_orders/Abertura"
                client = RequestClient(
                    url=url,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    request_data=payload,
                )
                result = client.send_api_request()

                if 'detail' in result:
                    messages.error(request, result['detail'])
                else:
                    messages.success(request, "OS criada com sucesso!")
                    return redirect('transportes:detalhe_os_transp', order_number=payload["order_number"])

            except:
                messages.error(
                    request, "Erro ao criar OS. Verifique os dados e tente novamente.")
                return redirect('transportes:criar_os')

    return render(request, 'transportes/transportes/criar_os.html', {
        'site_title': titulo,
        'form': form,
        'botao_texto': 'Criar OS',

    })
