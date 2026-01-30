from django.shortcuts import render, redirect
from ...forms import CheckoutReverseCreateForm
from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient
from django.contrib import messages

JSON_CT = "application/json"

MAX_KITS_PER_VOLUME = 2
MAX_VOLUMES = 10


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
                "client": "cielo",
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

    return render(
        request,
        'logistica/templates_checkin_checkout/checkout_reverse_create.html', {
            'form': form,
            'botao_texto': 'Inserir',
            'site_title': titulo,
            'romaneio': result,
        }
    )
