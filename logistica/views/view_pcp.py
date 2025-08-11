from django.shortcuts import render
from django.http import HttpResponse
from ..forms import PcpForm

def pcp(request):
    form = PcpForm(request.POST or None)

    return render(request, "logistica/pcp.html", {
        "form": form,
        "etapa_ativa": "pcp",
        'botao_texto': 'Enviar',
    })