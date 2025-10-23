from ..forms import OrderSelectForm
from django.shortcuts import render, redirect


def order_select(request):
    titulo = "Seleção de Pedido"

    if request.method == "POST":
        form = OrderSelectForm(request.POST, nome_form=titulo)
        if form.is_valid():
            order = form.cleaned_data['order']
            action = form.cleaned_data['actions']

            request.session['order'] = order

            if action == "checkin":
                return redirect('logistica:client_checkin')
            elif action == "desinstalar":
                return redirect('logistica:consultar_romaneio')
            elif action == "retirada":
                return redirect('logistica:order_return_check')
            elif action == "entrega":
                return redirect('logistica:detalhe_pedido', order=order)
            else:
                return redirect('logistica:detalhe_pedido', order=order)
    else:
        form = OrderSelectForm(nome_form=titulo)

    return render(request, 'logistica/order_select.html', {
        'form': form,
        'site_title': titulo,
        'botao_texto': "Selecionar Pedido",
    })
