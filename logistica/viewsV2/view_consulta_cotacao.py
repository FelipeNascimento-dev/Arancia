from django.shortcuts import render, redirect
from ..forms import ConsultaQuoteForm
from utils.request import RequestClient
from django.contrib import messages
import json
from setup.local_settings import API_URL
from django.contrib.auth.decorators import login_required, permission_required
from datetime import datetime, timedelta
from django.utils import timezone

JSON_CT = "application/json"


def consulta_cotacao(request, numero_rom):
    titulo = "Consulta de DACE"
    form = ConsultaQuoteForm(request.POST,
                             nome_form=titulo,
                             initial={
                                 "numero_romaneio": numero_rom})
    result = {}
    show_cancel_modal = False

    if request.method == 'POST':
        romaneio_number = request.POST.get('numero_romaneio') or numero_rom
        if "enviar_evento" in request.POST:
            url = f"{API_URL}/api/v2/reverse/quote/{romaneio_number}/?refresh=false"
            client = RequestClient(
                url=url,
                method="GET",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": "application/json"
                },
            )

            result = client.send_api_request()

            print(result)

            if 'detail' in result:
                messages.error(request, result.get('detail'))
            else:
                messages.success(request, "Consulta realizada com sucesso!")

            if result and result.get("dace_list"):
                for dace in result["dace_list"]:
                    response_data = dace.get("response")

                    if isinstance(response_data, str):
                        try:
                            dace["response"] = json.loads(response_data)
                        except json.JSONDecodeError:
                            dace["response"] = {}
                    elif response_data is None:
                        dace["response"] = {}

            if result and result.get("payload"):
                result["payload_pretty"] = json.dumps(
                    result["payload"],
                    indent=4,
                    ensure_ascii=False
                )
            else:
                result["payload_pretty"] = ""

            result["quote_date_formatada"] = ""
            result["quote_hours_elapsed"] = None
            result["bloquear_pdf_dace"] = False
            result["aviso_impressao_dace"] = ""

            quote_date_str = result.get("quote_date")
            if quote_date_str:
                try:
                    quote_date = datetime.fromisoformat(quote_date_str)

                    if timezone.is_naive(quote_date):
                        quote_date = timezone.make_aware(
                            quote_date,
                            timezone.get_current_timezone()
                        )

                    agora = timezone.localtime()
                    quote_date_local = timezone.localtime(quote_date)

                    diff = agora - quote_date_local
                    horas_decorridas = diff.total_seconds() / 3600

                    result["quote_date_formatada"] = quote_date_local.strftime(
                        "%d/%m/%Y %H:%M:%S")
                    result["quote_hours_elapsed"] = round(horas_decorridas, 2)
                    result["bloquear_pdf_dace"] = horas_decorridas >= 12
                    result["aviso_impressao_dace"] = (
                        "A DACE deve ser impressa em até 12 horas a partir da criação da cotação."
                    )

                except Exception:
                    result["quote_date_formatada"] = quote_date_str
                    result["quote_hours_elapsed"] = None
                    result["bloquear_pdf_dace"] = True
                    result["aviso_impressao_dace"] = (
                        "Não foi possível validar a data da cotação. O PDF foi bloqueado por segurança."
                    )

        if "atualizar_dce" in request.POST:
            url = f"{API_URL}/api/v2/reverse/quote/{romaneio_number}/?refresh=true"
            client = RequestClient(
                url=url,
                method="GET",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": "application/json"
                },
            )

            result = client.send_api_request()

            if 'detail' in result:
                messages.error(request, result.get('detail'))
            else:
                messages.success(request, "DACE atualizada com sucesso!")

            if result and result.get("dace_list"):
                for dace in result["dace_list"]:
                    response_data = dace.get("response")

                    if isinstance(response_data, str):
                        try:
                            dace["response"] = json.loads(response_data)
                        except json.JSONDecodeError:
                            dace["response"] = {}
                    elif response_data is None:
                        dace["response"] = {}

            if result and result.get("payload"):
                result["payload_pretty"] = json.dumps(
                    result["payload"],
                    indent=4,
                    ensure_ascii=False
                )
            else:
                result["payload_pretty"] = ""

            result["quote_date_formatada"] = ""
            result["quote_hours_elapsed"] = None
            result["bloquear_pdf_dace"] = False
            result["aviso_impressao_dace"] = ""

            quote_date_str = result.get("quote_date")
            if quote_date_str:
                try:
                    quote_date = datetime.fromisoformat(quote_date_str)

                    if timezone.is_naive(quote_date):
                        quote_date = timezone.make_aware(
                            quote_date,
                            timezone.get_current_timezone()
                        )

                    agora = timezone.localtime()
                    quote_date_local = timezone.localtime(quote_date)

                    diff = agora - quote_date_local
                    horas_decorridas = diff.total_seconds() / 3600

                    result["quote_date_formatada"] = quote_date_local.strftime(
                        "%d/%m/%Y %H:%M:%S")
                    result["quote_hours_elapsed"] = round(horas_decorridas, 2)
                    result["bloquear_pdf_dace"] = horas_decorridas >= 12
                    result["aviso_impressao_dace"] = (
                        "A DACE deve ser impressa em até 12 horas a partir da criação da cotação."
                    )

                except Exception:
                    result["quote_date_formatada"] = quote_date_str
                    result["quote_hours_elapsed"] = None
                    result["bloquear_pdf_dace"] = True
                    result["aviso_impressao_dace"] = (
                        "Não foi possível validar a data da cotação. O PDF foi bloqueado por segurança."
                    )

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
                messages.success(request, "Cotação cancelada com sucesso!")

        if "criar_pedido" in request.POST:
            quote_id = request.POST.get("quote_id")

            create_payload = {
                "quote_id": quote_id,
                "created_by": request.user.username
            }
            create_url = f"{API_URL}/api/v2/reverse/order/new/"
            create_client = RequestClient(
                url=create_url,
                method="POST",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": "application/json"
                },
                request_data=create_payload
            )

            create_result = create_client.send_api_request()

            print(create_payload)
            order = create_result.get('order_number')

            if 'detail' in create_result:
                messages.error(request, create_result.get('detail'))
            else:
                messages.success(request, "Pedido criado com sucesso!")
                return redirect('logistica:detalhe_pedido', order=order)

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
