from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from logistica.forms.forms_reverse.forms_lista_romaneios import ListaRomaneiosForm


def lista_romaneios(request):
    titulo = "Lista de Romaneios"
    form = ListaRomaneiosForm(request.POST or None, nome_form=titulo)

    if request.method == 'POST':
        if "enviar_evento" in request.POST:
            pass

    return render(request, 'logistica/templatesV2/lista_romaneios.html', {
        'botao_texto': 'Listar',
        'site_title': titulo,
        'form': form,
    })
