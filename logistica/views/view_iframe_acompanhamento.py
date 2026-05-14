from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import AcompanhamentoSistema


@login_required
def acompanhamento_iframe(request, slug):
    acompanhamento = get_object_or_404(
        AcompanhamentoSistema,
        slug=slug,
        ativo=True
    )

    context = {
        "acompanhamento": acompanhamento,
    }

    return render(request, "logistica/acompanhamento_iframe.html", context)
