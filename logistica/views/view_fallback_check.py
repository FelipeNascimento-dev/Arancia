from ..forms import FallbackCheckForm
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def fallback_check(request):
    form = FallbackCheckForm(request.POST or None,
                             name_form="Conferir Volume de Retirada")
    return render(request, 'logistica/fallback_check.html', {
        'form': form,
        'name_form': "Conferir Volume de Retirada",
        'botao_texto': "Conferir",
    })
