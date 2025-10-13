from ..forms import ClientSelectForm
from django.shortcuts import render


def client_select(request):
    titulo = "Seleção de Cliente"

    form = ClientSelectForm(request.POST, nome_form=titulo)

    if request.method == 'POST':
        form = ClientSelectForm(request.POST, nome_form=titulo)
    else:
        form = ClientSelectForm(nome_form=titulo)
    return render(request, 'logistica/client_select.html', {
        'form': form,
        'site_title': titulo,
        'botao_texto': 'Consultar Cliente'
    })
