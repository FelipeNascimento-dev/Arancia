from ..forms import UnsuccessfulForm
from django.shortcuts import render, redirect


def unsuccessful(request):
    titulo = 'Fluxo de Insucesso'

    if request.method == 'POST':
        form = UnsuccessfulForm(request.POST, nome_form=titulo)

        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            return redirect('logistica:detalhe_pedido', order=pedido)

    else:
        form = UnsuccessfulForm(nome_form=titulo)

    return render(
        request, 'logistica/unsuccessful.html', {
            'form': form,
            'botao_texto': 'Receber Insucesso',
            'site_title': titulo,
        })
