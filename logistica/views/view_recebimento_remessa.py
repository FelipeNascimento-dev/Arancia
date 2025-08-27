from django.shortcuts import render
from ..forms import RecebimentoRemessaForm


def recebimento_remessa(request):
    titulo = 'Recebimento por Remessa'
    form = RecebimentoRemessaForm(nome_form=titulo,)
    return render(request, "logistica/recebimento_remessa.html", {
        "form": form,
        "botao_texto": 'Consultar'
    })
