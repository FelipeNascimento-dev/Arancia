from ..forms import ConsultaResultEC01Form
from django.shortcuts import render, redirect

def consulta_ec01(request):
    form = ConsultaResultEC01Form()
    return render(request, 'arancia/consulta_result_ec01.html', {'form': form})