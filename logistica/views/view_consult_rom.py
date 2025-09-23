from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import RomaneioConsultaForm


def consult_rom(request):
    titulo = 'Consultar Romaneio'
    proximo_disponivel = None

    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero"]

            request.session["romaneio_num"] = numero
            return redirect("logistica:reverse_create")
    else:
        form = RomaneioConsultaForm(nome_form=titulo)

    return render(request, "logistica/consult_rom.html", {
        "form": form,
        "botao_texto": 'Consultar',
        "proximo_disponivel": proximo_disponivel,
        "site_title": 'Consulta de Romaneio',
    })
