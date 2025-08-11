from django.shortcuts import render
from django.http import HttpResponse
from ..forms import trackingIPForm

def trackingIP(request):
    titulo = 'IP - PCP' 
    form = trackingIPForm(request.POST or None, nome_form=titulo, show_serial=False)

    return render(request, "logistica/pcp.html", {
        "form": form,
        "etapa_ativa": "pcp",
        'botao_texto': 'Enviar',
    })