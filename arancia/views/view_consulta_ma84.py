from ..forms import ConsultaResultMA84Form
from django.shortcuts import render, redirect

def consulta_ma84(request):
    form = ConsultaResultMA84Form()
    return render(request, 'arancia/consulta_result_ma84.html', {'form': form})