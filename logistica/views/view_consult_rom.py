from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import RomaneioReverse
from ..forms import RomaneioConsultaForm


def consult_rom(request):
    titulo = 'Consultar Romaneio'

    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero"]

            romaneio, criado = RomaneioReverse.objects.get_or_create(
                numero=numero)

            request.session["romaneio_num"] = romaneio.numero

            return redirect("logistica:reverse_create")
    else:
        form = RomaneioConsultaForm(nome_form=titulo,)

    return render(request, "logistica/consult_rom.html", {
        "form": form,
        "botao_texto": 'Consultar',
    })
