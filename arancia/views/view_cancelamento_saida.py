from ..forms import CancelamentoSaidaCampoForm
from django.shortcuts import render, redirect

def cancelamento_saida_campo(request):
    form = CancelamentoSaidaCampoForm()
    return render(request, 'arancia/cancelamento_saida_campo.html', {'form': form})