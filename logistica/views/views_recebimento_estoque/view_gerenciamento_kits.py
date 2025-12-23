from django.shortcuts import render, redirect
from ...forms import GerenciamentoKitsForm


def gerenciamento_kits(request):
    titulo = 'Gerenciamento de Kits'

    if 'kits' not in request.session:
        request.session['kits'] = []

    kits = request.session['kits']

    if request.method == 'POST':
        form = GerenciamentoKitsForm(request.POST, nome_form=titulo)
        if form.is_valid():
            kit = {
                "serial": form.cleaned_data['serial_number'],
                "chip": form.cleaned_data['chip_number'],
            }

            kits.append(kit)
            request.session['kits'] = kits
            request.session.modified = True

            return redirect('logistica:gerenciamento_kits')
    else:
        form = GerenciamentoKitsForm(nome_form=titulo)

    return render(request, 'logistica/templates_recebimento_estoque/gerenciamento_kits.html', {
        "form": form,
        "site_title": titulo,
        "kits": kits,
        "botao_texto": 'Adicionar Kit'
    })
