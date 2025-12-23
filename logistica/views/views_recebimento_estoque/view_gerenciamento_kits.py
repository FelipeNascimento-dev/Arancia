from django.shortcuts import render, redirect
from ...forms import GerenciamentoKitsForm


def gerenciamento_kits(request):
    titulo = 'Gerenciamento de Kits'

    if 'kits' not in request.session:
        request.session['kits'] = []

    kits = request.session['kits']
    edit_index = None

    if request.method == 'POST' and 'delete_index' in request.POST:
        index = int(request.POST.get('delete_index'))
        if 0 <= index < len(kits):
            kits.pop(index)
            request.session.modified = True
        return redirect('logistica:gerenciamento_kits')

    if request.method == 'POST' and 'edit_index' in request.POST:
        edit_index = int(request.POST.get('edit_index'))
        kit = kits[edit_index]
        form = GerenciamentoKitsForm(
            initial={
                'serial_number': kit['serial'],
                'chip_number': kit['chip'],
            },
            nome_form=titulo
        )

    elif request.method == 'POST':
        form = GerenciamentoKitsForm(request.POST, nome_form=titulo)
        if form.is_valid():
            kit_data = {
                "serial": form.cleaned_data['serial_number'],
                "chip": form.cleaned_data['chip_number'],
            }

            if 'save_edit_index' in request.POST:
                index = int(request.POST.get('save_edit_index'))
                kits[index] = kit_data
            else:
                kits.append(kit_data)

            request.session.modified = True
            return redirect('logistica:gerenciamento_kits')

    else:
        form = GerenciamentoKitsForm(nome_form=titulo)

    return render(request, 'logistica/templates_recebimento_estoque/gerenciamento_kits.html', {
        "form": form,
        "site_title": titulo,
        "kits": kits,
        "edit_index": edit_index,
        "botao_texto": 'Salvar Alteração' if edit_index is not None else 'Adicionar Kit'
    })
