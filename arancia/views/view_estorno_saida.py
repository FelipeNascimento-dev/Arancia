from ..forms import EstornoSaidaCampoForm
from django.shortcuts import render, redirect

def estorno_saida_campo(request):
    form = EstornoSaidaCampoForm()
    return render(request, 'arancia/estorno_reserva.html', {'form': form})