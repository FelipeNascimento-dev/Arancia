from ..forms import SaidaCampoForm
from django.shortcuts import render, redirect

def saida_campo(request):
    form = SaidaCampoForm()
    return render(request, 'arancia/reserva_equip.html', {'form': form})