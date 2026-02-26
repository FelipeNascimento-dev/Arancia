from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from ...forms import CheckoutReverseCreateForm
from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient
from django.contrib import messages
from datetime import datetime

JSON_CT = "application/json"

MAX_KITS_PER_VOLUME = 25
MAX_VOLUMES = 10


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def checkout_reverse_create(request, rom):
    numero_romaneio = rom
    user = request.user
    sales_channel = user.designacao.informacao_adicional.sales_channel
    if sales_channel == 'all':
        location_id = 0
    else:
        location_id = user.designacao.informacao_adicional_id

    titulo = f'Romaneio {numero_romaneio}'
    form = CheckoutReverseCreateForm(request.POST or None, nome_form=titulo)

    client_code = request.session.get("client_code")
    client_name = request.session.get("client_name")

    result = None

    try:
        url_get = f"{STOCK_API_URL}/v1/romaneios/{numero_romaneio}?location_id={location_id}"
        client_get = RequestClient(
            url=url_get,
            method="GET",
            headers={"Accept": JSON_CT},
        )
        result = client_get.send_api_request()

        if 'detail' in result:
            messages.error(request, result.get('detail'))
    except Exception as e:
        messages.error(request, f'Erro ao consultar romaneio: {e}')

    if request.method == "POST" and 'enviar_evento' in request.POST:
        if form.is_valid():
            serial = form.cleaned_data["serial"]

            volums = result.get("volums", [])

            volume_number = None
            kit_number = None

            for volume in volums:
                kits = volume.get("kits", [])
                if len(kits) < MAX_KITS_PER_VOLUME:
                    volume_number = int(volume.get("volum_number"))
                    kit_number = len(kits) + 1
                    break

            if volume_number is None:
                if len(volums) >= MAX_VOLUMES:
                    messages.error(
                        request, "Limite máximo de volumes atingido"
                    )
                    return redirect(request.path)

                volume_number = len(volums) + 1
                kit_number = 1

            payload = {
                "serial": serial,
                "volume_number": str(volume_number),
                "kit_number": str(kit_number),
                "client": client_code,
                "location_id": location_id,
                "create_by": user.username,
            }

            client_post = RequestClient(
                url=f"{STOCK_API_URL}/v1/romaneios/insert-items/{numero_romaneio}",
                method="POST",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": JSON_CT,
                },
                request_data=payload,
            )

            result_post = client_post.send_api_request()

            if isinstance(result_post, dict) and "detail" not in result_post:
                messages.success(
                    request, f"Serial {serial} inserido com sucesso")
            else:
                messages.error(request, result_post.get(
                    "detail", "Erro ao inserir serial"))

            return redirect(request.path)

    if request.method == "POST" and 'remove_serial' in request.POST:
        serial = request.POST.get("serial")

        if not serial:
            messages.error(request, "Serial inválido")
            return redirect(request.path)

        client_delete = RequestClient(
            url=f"{STOCK_API_URL}/v1/romaneios/{numero_romaneio}/?serial={serial}",
            method="DELETE",
            headers={"Accept": JSON_CT},
        )

        result_delete = client_delete.send_api_request()

        if isinstance(result_delete, dict) and "detail" not in result_delete:
            messages.success(
                request, f"Serial {serial} removido com sucesso"
            )
        else:
            messages.error(
                request,
                result_delete.get("detail", "Erro ao remover serial")
            )

        return redirect(request.path)

    if request.method == "POST" and 'cancelar_romaneio' in request.POST:
        payload_put = {
            "status_rom": "CANCELADO",
            "update_by": user.username,
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }

        url_put = f"{STOCK_API_URL}/v1/romaneios/{numero_romaneio}"

        client_put = RequestClient(
            url=url_put,
            method="PUT",
            headers={
                "Accept": JSON_CT,
                "Content-Type": JSON_CT,
            },
            request_data=payload_put
        )

        result_put = client_put.send_api_request()

        if isinstance(result_put, dict) and "detail" not in result_put:
            messages.success(request, "Romaneio cancelado com sucesso")
        else:
            messages.error(
                request,
                result_put.get("detail", "Erro ao cancelar romaneio")
            )

        return redirect(request.path)

    if request.method == "POST" and 'finalizar_romaneio' in request.POST:

        if result.get("status") != "ABERTO":
            messages.error(request, "Romaneio não pode ser finalizado.")
            return redirect(request.path)

        payload_finish = {
            "finished_by": user.username,
            "finished_at": datetime.utcnow().isoformat() + "Z",
            "movement_type": "RETURN",
            "external_order_number": numero_romaneio
        }

        url_finish = (
            f"{STOCK_API_URL}/v2/romaneios/finish/{numero_romaneio}?location_id={location_id}"
        )

        client_finish = RequestClient(
            url=url_finish,
            method="POST",
            headers={
                "Accept": JSON_CT,
                "Content-Type": JSON_CT,
            },
            request_data=payload_finish
        )

        print(payload_finish)

        result_finish = client_finish.send_api_request()

        if isinstance(result_finish, dict) and "detail" not in result_finish:
            messages.success(request, "Romaneio finalizado com sucesso")
        else:
            messages.error(
                request,
                result_finish.get("detail", "Erro ao finalizar romaneio")
            )

        return redirect(request.path)

    return render(
        request,
        'logistica/templates_checkin_checkout/checkout_reverse_create.html', {
            'form': form,
            'botao_texto': 'Inserir',
            'site_title': titulo,
            'romaneio': result,
            'disable_enviar_evento': result.get("status") != "ABERTO",
            "current_parent_menu": "logistica",
            "current_menu": "checkout",
            "current_submenu": "iniciar_checkout"
        }
    )
