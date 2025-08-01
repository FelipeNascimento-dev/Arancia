from ..forms import EstornoReservaForms
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_credenciado', raise_exception=True)
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
@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def estorno_reserva(request):
    serial_inserido = request.session.pop('serial_recebido', None)

    if request.method == 'POST':
        form = EstornoReservaForms(request.POST)

        if form.data.get('tp_reg') == '84' and form.data.get('serial') == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/estorno_reserva.html', {'form': form})

        if form.is_valid():
            request.session['serial_inserido'] = form.cleaned_data

            return redirect('logistica:consulta_result_ma', tp_reg='85')

    else:
        form = EstornoReservaForms()

    return render(request, 'logistica/estorno_reserva.html', {
        'form': form,
        'etapa_ativa': 'estorno_reserva'
    })
