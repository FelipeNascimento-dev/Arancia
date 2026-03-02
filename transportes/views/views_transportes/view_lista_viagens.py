from django.shortcuts import render
from ...forms import ListaViagensForm


def lista_viagens(request):
    titulo = "Lista de Viagens"

    form = ListaViagensForm(request.POST, nome_form=titulo)

    return render(request, 'transportes/transportes/lista_viagens.html', {
        "botao_texto": 'Consultar',
        "site_title": titulo,
        "form": form,
    })
