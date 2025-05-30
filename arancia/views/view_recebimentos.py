from django.shortcuts import render
from ..forms import PreRecebimentoForm, RecebimentoForm

def pre_recebimento(request):
    form = PreRecebimentoForm()
    return render(request, 'arancia/pre_recebimento.html', {'form': form})

def recebimento(request):
    form = RecebimentoForm()
    return render(request, 'arancia/recebimento.html', {'form': form})
