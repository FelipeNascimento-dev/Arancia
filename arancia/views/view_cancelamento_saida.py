from ..forms import CancelamentoSaidaCampoForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

def buscar_dados(form):
    return [
        {
            "nr_arq": "00000019",
            "mensagem": "Erro no processamento",
            "status": "3",
            "data": "2025-05-27",
            "hora": "17:13:32",
        }
    ]

@csrf_protect
def cancelamento_saida_campo(request):
    serial_inserido = request.session.pop('serial_recebido', None)

    if request.method == 'POST':
        form = CancelamentoSaidaCampoForm(request.POST)

        if form.data.get('tp_reg') == '85' and form.data.get('serial') == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'arancia/estorno_reserva.html', {'form': form})

        if form.is_valid():
            request.session['serial_inserido'] = form.cleaned_data

            return redirect('arancia:consulta_result_ma', tp_reg='85')

    else:
        form = CancelamentoSaidaCampoForm()

    return render(request, 'arancia/estorno_reserva.html', {
        'form': form
    })