from django.db.models import Max
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import RomaneioReverse
from ..forms import RomaneioConsultaForm


def consult_rom(request):
    titulo = 'Consultar Romaneio'
    proximo_disponivel = None

    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero"]

            try:
                romaneio = RomaneioReverse.objects.get(numero=numero)
                request.session["romaneio_num"] = romaneio.numero
                return redirect("logistica:reverse_create")

            except RomaneioReverse.DoesNotExist:
                ultimo = RomaneioReverse.objects.aggregate(
                    ultimo=Max("numero"))["ultimo"]

                if ultimo:
                    proximo_disponivel = str(int(ultimo) + 1).zfill(10)
                else:
                    proximo_disponivel = "0000000001"

                messages.warning(
                    request,
                    f"O romaneio {numero} não existe. Você pode criar o próximo disponível: {proximo_disponivel}"
                )

                request.session["romaneio_num"] = proximo_disponivel
    else:
        form = RomaneioConsultaForm(nome_form=titulo,)

    return render(request, "logistica/consult_rom.html", {
        "form": form,
        "botao_texto": 'Consultar',
        "proximo_disponivel": proximo_disponivel,
    })
