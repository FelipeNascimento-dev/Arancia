from django.shortcuts import render
from ..forms import UnsuccessfulInsertForm


def unsuccessful_insert(request):
    titulo = 'Recebimento de Insucesso'
    if request.method == 'POST':
        form = UnsuccessfulInsertForm(request.POST, nome_form=titulo)
    else:
        form = UnsuccessfulInsertForm(nome_form=titulo)

    return render(request, 'logistica/unsuccessful_insert.html', {
        'form': form,
        'botao_texto': 'Registrar Insucesso',
        'site_title': titulo,
    })
