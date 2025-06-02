from ..forms import ReservaEquipamentosForm
from django.shortcuts import render, redirect

def reserva_equip(request):
    form = ReservaEquipamentosForm()
    return render(request, 'arancia/reserva_equip.html', {'form': form})