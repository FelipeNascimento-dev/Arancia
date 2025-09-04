from ..forms import OrderReturnCheckForm
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

SAIDA_SERIALS_KEY = "saida_serials"

CARRY_PEDIDO_KEY = "carry_pedido_next"


def _mark_carry_next(request):
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True


def _consume_carry_next(request) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


def fallback_get_serials(request) -> list[str]:
    return request.session.get(SAIDA_SERIALS_KEY, [])


def fallback_save_serials(request, serials: list[str]) -> None:
    request.session[SAIDA_SERIALS_KEY] = serials
    request.session.modified = True


def saida_dedup_upper(values) -> list[str]:
    seen = set()
    out = []
    for v in values or []:
        s = (v or "").strip().upper()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def order_return_check(request):
    form = OrderReturnCheckForm(request.POST or None,
                                name_form="Conferir Volume de Retirada")
    return render(request, 'logistica/order_return_check.html', {
        'form': form,
        'name_form': "Conferir Volume de Retirada",
        'site_title': "Conferir Volume de Retirada",
        'botao_texto': "Conferir",
    })
