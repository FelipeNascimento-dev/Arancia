from django.shortcuts import render, redirect
from django.contrib import messages
from ...forms import UnsuccessfulInsertForm
from utils.request import RequestClient
from setup.local_settings import API_URL
from django.contrib.auth.decorators import login_required, permission_required

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def unsuccessful_insert(request, order=None):
    titulo = 'Recebimento de Insucesso'

    key_good = 'unsuccessful_serials_good'
    key_bad = 'unsuccessful_serials_bad'

    serials_good = request.session.get(key_good, [])
    serials_bad = request.session.get(key_bad, [])

    serials_display = serials_good + serials_bad

    numero_pedido = order or request.GET.get('order')

    if request.method == 'POST':
        form = UnsuccessfulInsertForm(request.POST, nome_form=titulo)

        if 'add_serial' in request.POST:
            if form.is_valid():
                serial = form.cleaned_data.get('serial', '').strip().upper()
                pedido = form.cleaned_data.get('pedido') or numero_pedido
                material = form.cleaned_data.get('material')

                if not serial:
                    messages.warning(request, "Digite um serial válido.")

                else:
                    if material == 'EC21':
                        if serial not in serials_good:
                            serials_good.append(serial)
                            request.session[key_good] = serials_good
                            messages.success(request, f"{serial} -> GOOD")
                        else:
                            messages.info(
                                request, f"{serial} já está em GOOD.")

                    elif material == 'EC22':
                        if serial not in serials_bad:
                            serials_bad.append(serial)
                            request.session[key_bad] = serials_bad
                            messages.success(request, f"{serial} -> BAD")
                        else:
                            messages.info(request, f"{serial} já está em BAD.")

                serials_display = serials_good + serials_bad

                form = UnsuccessfulInsertForm(
                    initial={'pedido': pedido, 'material': material},
                    nome_form=titulo
                )

        elif 'remove_serial' in request.POST:
            index = int(request.POST.get('remove_serial'))

            if index < len(serials_good):
                removido = serials_good.pop(index)
                request.session[key_good] = serials_good
                messages.info(request, f"{removido} removido de GOOD.")
            else:
                real_index = index - len(serials_good)
                if real_index < len(serials_bad):
                    removido = serials_bad.pop(real_index)
                    request.session[key_bad] = serials_bad
                    messages.info(request, f"{removido} removido de BAD.")

            serials_display = serials_good + serials_bad
            form = UnsuccessfulInsertForm(request.POST, nome_form=titulo)

        elif 'clear_serials' in request.POST:
            serials_good = []
            serials_bad = []
            request.session[key_good] = []
            request.session[key_bad] = []
            serials_display = []
            messages.info(request, "Lista de seriais limpa.")

            form = UnsuccessfulInsertForm(
                initial={'pedido': numero_pedido},
                nome_form=titulo
            )

        elif 'enviar_evento' in request.POST:
            if form.is_valid():
                pedido = form.cleaned_data.get('pedido') or numero_pedido
                material = form.cleaned_data.get('material')
                user = request.user
                location_id = user.designacao.informacao_adicional_id

                if not serials_good and not serials_bad:
                    messages.error(request, "Nenhum serial foi inserido.")
                    return redirect(request.path)

                url = f"{API_URL}/api/v2/trackings/send"

                if serials_good:
                    payload_good = {
                        "order_number": pedido,
                        "volume_number": 1,
                        "order_type": "FAILURE",
                        "tracking_code": "207",
                        "created_by": str(request.user),
                        "bar_codes": serials_good,
                        "from_location_id": location_id,
                        "to_location_id": location_id,
                        "equipament_state": "GOOD"
                    }
                    print("Payload GOOD:", payload_good)

                    client_good = RequestClient(
                        url=url,
                        method="POST",
                        headers={"Accept": JSON_CT},
                        request_data=payload_good
                    )

                    result_good = client_good.send_api_request()

                    if isinstance(result_good, dict) and result_good.get('detail'):
                        messages.error(request, f"{result_good['detail']}")
                    else:
                        messages.success(
                            request, "Insucesso registrado com sucesso!")

                    for s in serials_good:
                        print(
                            f"GOOD → Pedido {pedido} | Serial {s} | Material {material}")

                if serials_bad:
                    payload_bad = {
                        "order_number": pedido,
                        "volume_number": 1,
                        "order_type": "FAILURE",
                        "tracking_code": "207",
                        "created_by": str(request.user),
                        "bar_codes": serials_bad,
                        "from_location_id": location_id,
                        "to_location_id": location_id,
                        "equipament_state": "BAD"
                    }

                    print("Payload BAD:", payload_bad)
                    client_bad = RequestClient(
                        url=url,
                        method="POST",
                        headers={"Accept": JSON_CT},
                        request_data=payload_bad
                    )

                    result_bad = client_bad.send_api_request()

                    if isinstance(result_bad, dict) and result_bad.get('detail'):
                        messages.error(request, f"{result_bad['detail']}")
                    else:
                        messages.success(
                            request, "Insucesso registrado com sucesso!")

                    for s in serials_bad:
                        print(
                            f"BAD → Pedido {pedido} | Serial {s} | Material {material}")

                request.session[key_good] = []
                request.session[key_bad] = []

                messages.success(request, "Envio concluído com sucesso!")
                return redirect('logistica:unsuccessful_insert', order=pedido)

            else:
                messages.error(request, "Preencha os campos obrigatórios.")

    else:
        form = UnsuccessfulInsertForm(
            initial={'pedido': numero_pedido},
            nome_form=titulo
        )

    if numero_pedido:
        form.fields['pedido'].widget.attrs['readonly'] = True

    return render(request, 'logistica/templates_fluxo_entrega/insucesso.html', {
        'form': form,
        'serials': serials_display,
        'botao_texto': 'Registrar Insucesso',
        'site_title': titulo,
        'etapa_ativa': 'unsuccessful_insert',
    })
