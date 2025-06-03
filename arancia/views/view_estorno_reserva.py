from ..forms import EstornoReservaForms
from django.shortcuts import render, redirect

def estorno_reserva(request):
    form = EstornoReservaForms()
    return render(request, 'arancia/estorno_reserva.html', {'form': form})