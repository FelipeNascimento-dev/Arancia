from ..forms import UnsuccessfulForm
from django.shortcuts import render, redirect


def unsuccessful(request):
    titulo = 'Fluxo de Insucesso'
    form = UnsuccessfulForm(nome_form=titulo)

    return render(
        request, 'logistica/unsuccessful.html', {
            'form': form,
            'botao_texto': 'Receber Insucesso',
            'site_title': titulo,
        })
