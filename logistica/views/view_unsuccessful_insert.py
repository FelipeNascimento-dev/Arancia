from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import UnsuccessfulInsertForm
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
def unsuccessful_insert(request, order=None):
    titulo = 'Recebimento de Insucesso'
    session_key = 'unsuccessful_serials'

    serials = request.session.get(session_key, [])

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
                elif serial in serials:
                    messages.info(
                        request, f"O serial {serial} já foi adicionado.")
                else:
                    serials.append(serial)
                    request.session[session_key] = serials
                    messages.success(
                        request, f"Serial {serial} adicionado com sucesso.")

                form = UnsuccessfulInsertForm(
                    initial={'pedido': pedido, 'material': material},
                    nome_form=titulo
                )

        elif 'remove_serial' in request.POST:
            index = int(request.POST.get('remove_serial'))
            if 0 <= index < len(serials):
                removido = serials.pop(index)
                request.session[session_key] = serials
                messages.info(request, f"Serial {removido} removido.")
            form = UnsuccessfulInsertForm(request.POST, nome_form=titulo)

        elif 'clear_serials' in request.POST:
            request.session[session_key] = []
            serials = []
            messages.info(request, "Todos os seriais foram limpos.")
            form = UnsuccessfulInsertForm(
                initial={'pedido': numero_pedido},
                nome_form=titulo
            )

        elif 'enviar_evento' in request.POST:
            if form.is_valid():
                pedido = form.cleaned_data.get('pedido') or numero_pedido
                material = form.cleaned_data.get('material')

                if not serials:
                    messages.error(request, "Nenhum serial foi inserido.")
                else:
                    for s in serials:
                        print(
                            f"Salvar -> Pedido {pedido} | Serial {s} | Material {material}")

                    request.session[session_key] = []
                    messages.success(
                        request, f"{len(serials)} seriais registrados com sucesso!")
                    return redirect('logistica:unsuccessful_insert', order=pedido)

            else:
                messages.error(
                    request, "Preencha os campos obrigatórios corretamente.")

    else:
        form = UnsuccessfulInsertForm(
            initial={'pedido': numero_pedido},
            nome_form=titulo
        )

    if numero_pedido:
        form.fields['pedido'].widget.attrs['readonly'] = True

    return render(request, 'logistica/unsuccessful_insert.html', {
        'form': form,
        'botao_texto': 'Registrar Insucesso',
        'site_title': titulo,
        'serials': serials,
        'etapa_ativa': 'unsuccessful_insert',
    })
