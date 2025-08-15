from ..forms import EtiquetasForm
from django.shortcuts import render, redirect
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest

def consulta_etiquetas(request):
    # Ex.: modo download (se tiver)
    if request.method == "GET" and request.GET.get("download") == "1":
        # ... gere o arquivo ...
        return HttpResponse(b"arquivo", content_type="text/plain")  # SEMPRE retorne

    if request.method == "POST":
        form = EtiquetasForm(request.POST)
        if form.is_valid():
            # ... faça o que precisar ...
            return redirect("logistica:alguma_rota")
        # form inválido -> renderiza com erros
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": form,
            'botao_texto': 'Consultar',
            })

    # GET normal -> sempre renderiza algo
    form = EtiquetasForm()
    return render(request, "logistica/consulta_etiquetas.html", {
        "form": form,
        'botao_texto': 'Consultar',
        })
