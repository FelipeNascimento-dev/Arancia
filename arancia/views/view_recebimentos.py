from django.shortcuts import render, redirect
from ..forms import PreRecebimentoForm, RecebimentoForm

def pre_recebimento(request):
    if request.method == 'POST':
        form = PreRecebimentoForm(request.POST)
        if form.is_valid():
            id_inserido = form.cleaned_data.get('id')
            request.session['id_pre_recebido'] = id_inserido
            request.session['origem'] = 'pre-recebimento'
            return redirect('arancia:consulta_resultados', tp_reg='13')
    else:
        form = PreRecebimentoForm()

    return render(request, 'arancia/pre_recebimento.html', {'form': form})

def recebimento(request):
    if request.method == 'POST':
        form = RecebimentoForm(request.POST)
        if form.is_valid():
            id_inserido = form.cleaned_data.get('id')
            serial_inserido = form.cleaned_data.get('serial')
            request.session['id_pre_recebido'] = id_inserido
            request.session['origem'] = 'recebimento'
            request.session['serial_recebido'] = serial_inserido
            return redirect('arancia:consulta_resultados', tp_reg='15')
    else:
        form = RecebimentoForm()
        
    return render(request, 'arancia/recebimento.html', {'form': form})
