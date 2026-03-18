from django.shortcuts import render, redirect
from ..forms import ConsultaQuoteForm
from utils.request import RequestClient
from django.contrib import messages
import json
from setup.local_settings import API_URL
from django.contrib.auth.decorators import login_required, permission_required

JSON_CT = "application/json"


def consulta_cotacao(request, numero_rom):
    titulo = "Consulta de DACE"
    form = ConsultaQuoteForm(request.POST,
                             nome_form=titulo,
                             initial={
                                 "numero_romaneio": numero_rom})
    result = []
    show_cancel_modal = False

    if request.method == 'POST':
        romaneio_number = request.POST.get('numero_romaneio')
        if "enviar_evento" in request.POST:
            url = f"{API_URL}/api/v2/reverse/quote/{romaneio_number}"
            client = RequestClient(
                url=url,
                method="GET",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": "application/json"
                },
            )

            result = client.send_api_request()

           # print(result)

            if 'detail' in result:
                messages.error(request, result.get('detail'))
            else:
                messages.success(request, "Consulta realizada com sucesso!")

            if result and result.get("payload"):
                result["payload_pretty"] = json.dumps(
                    result["payload"],
                    indent=4,
                    ensure_ascii=False
                )
            else:
                result["payload_pretty"] = ""

        if "cancelar_cotacao" in request.POST:
            show_cancel_modal = True

        if "confirmar_cancelamento" in request.POST:
            cancelar_romaneio = "cancelar_romaneio" in request.POST
            romaneio_number = request.POST.get('numero_romaneio')

            # cancel_payload = {
            #     "romaneio_number": romaneio_number,
            #     "cancell_rom": cancelar_romaneio,
            # }

            # print(cancel_payload)

            cancel_url = f"{API_URL}/api/v2/reverse/quote/cancell/?romaneio_number={romaneio_number}&cancell_rom={cancelar_romaneio}"
            cancel_client = RequestClient(
                url=cancel_url,
                method="POST",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": "application/json"
                },
            )

            cancel_result = cancel_client.send_api_request()

            if 'detail' in cancel_result:
                messages.error(request, cancel_result.get('detail'))
            else:
                messages.succes(request, "Cotação cancelada com sucesso!")

    else:
        form = ConsultaQuoteForm(
            initial={"numero_romaneio": numero_rom},
            nome_form=titulo
        )

    return render(request, "logistica/templatesV2/consulta_cotacao.html", {
        'form': form,
        'site_title': titulo,
        'botao_texto': 'Consultar',
        'dace_data': result,
        'show_cancel_modal': show_cancel_modal,
    })
