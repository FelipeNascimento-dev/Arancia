from django.shortcuts import render
from ..forms import RecebimentoRemessaForm


def recebimento_remessa(request):
    form = RecebimentoRemessaForm()
    return render(request, "logistica/recebimento_remessa.html", {
        "form": form
    })
