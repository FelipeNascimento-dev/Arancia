from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import RomaneioReverse
from ..forms import RomaneioConsultaForm


def consult_rom(request):
    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero"]

            romaneio, criado = RomaneioReverse.objects.get_or_create(
                numero=numero)

            if criado:
                messages.success(
                    request, f"Romaneio {numero} criado com sucesso!")
            else:
                messages.info(request, f"Romaneio {numero} já existe.")

            return redirect("reverse_create", pk=romaneio.pk)
    else:
        form = RomaneioConsultaForm()

    return render(request, "logistica/consult_rom.html", {
        "form": form,
        "botao_texto": 'Consultar',
    })
