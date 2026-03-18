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
    })
