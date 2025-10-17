from ..forms import OrderSelectForm
from django.shortcuts import render


def order_select(request):
    titulo = "Seleção de Pedido"

    if request.method == "POST":
        form = OrderSelectForm(request.POST, nome_form=titulo)
    else:
        form = OrderSelectForm(request.POST, nome_form=titulo)

    return render(request, 'logistica/order_select.html', {
        'form': form,
        'site_title': titulo,
        'botao_texto': 'Selecionar Ação'
    })
