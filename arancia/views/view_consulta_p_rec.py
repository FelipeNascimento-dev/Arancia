from ..forms import ConsultaPreRecebimentoForm
from django.shortcuts import render

def consulta_pre_recebimento(request):
    form = ConsultaPreRecebimentoForm()
    return render(request, 'arancia/consulta_p_rec.html', {'form': form})