from django.shortcuts import render, redirect
from ..forms import ReverseCreateForm


def reverse_create(request):
    titulo = 'Reversa de Equipamento'
    form = ReverseCreateForm(nome_form=titulo)

    context = {
        'form': form,
        'botao_texto': 'Inserir',
        'site_title': 'Reversa',
    }
    return render(request, 'logistica/reverse_create.html', context)
