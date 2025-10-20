from ..forms import OrderSelectForm
from django.shortcuts import render, redirect


def order_select(request):
    titulo = "Seleção de Pedido"

    if request.method == "POST":
        form = OrderSelectForm(request.POST, nome_form=titulo)
        if form.is_valid():
            request.session['order'] = form.cleaned_data['order']
        return redirect('logistica:detalhe_pedido', order=form.cleaned_data['order'])
    else:
        form = OrderSelectForm(request.POST, nome_form=titulo)

    return render(request, 'logistica/order_select.html', {
        'form': form,
        'site_title': titulo,
        'botao_texto': "Selecionar Pedido",
    })
