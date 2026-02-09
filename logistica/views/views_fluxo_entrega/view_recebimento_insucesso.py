from ...forms import RecebimentoInsucessoForm
from django.shortcuts import render, redirect
from django.contrib import messages
from setup.local_settings import API_URL
from utils.request import RequestClient


JSON_CT = "application/json"


def recebimento_insucesso(request):
    titulo = "Recebimento Insucesso"
    form = RecebimentoInsucessoForm(request.POST, nome_form=titulo)
    pedido = request.POST.get('pedido')
    modal_insucesso = False

    if request.method == 'POST':
        if 'enviar_evento' in request.POST:
            if form.is_valid():
                modal_insucesso = True
            else:
                messages.error(
                    request, "Por favor, insira um numero de pedido.")

        if 'confirm_insucesso' in request.POST:
            payload = {
                "order_number": pedido,
                "volume_number": 1,
                "order_type": "FAILURE",
                "tracking_code": "206",
                "created_by": request.user.username,
            }

            client = RequestClient(
                url=f"{API_URL}/api/v2/trackings/send",
                method="POST",
                headers={"Accept": JSON_CT, "Content-Type": JSON_CT},
                request_data=payload
            )
            result = client.send_api_request()

            if 'detail' in result:
                messages.error(request, f"Erro: {result['detail']}")
            else:
                messages.success(
                    request, "Evento de Recebimento Insucesso enviado com sucesso.")

            return redirect('logistica:unsuccessful_insert', order=pedido)

    return render(
        request,
        'logistica/templates_fluxo_entrega/recebimento_insucesso.html',
        {
            'titulo': titulo,
            'form': form,
            'botao_texto': 'Receber Insucesso',
            'site_title': titulo,
            'modal_insucesso': modal_insucesso,
            "current_parent_menu": "logistica",
            "current_menu": "lastmile",
            "current_submenu": "entrega_simplificada",
            "current_subsubmenu": "insucesso"
        }
    )
