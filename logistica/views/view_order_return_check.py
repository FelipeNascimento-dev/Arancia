from ..forms import OrderReturnCheckForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect

ORDER_RETURN_SERIALS_KEY = "order_return_serials"

CARRY_PEDIDO_KEY = "carry_pedido_next"


def _mark_carry_next(request):
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True


def _consume_carry_next(request) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


def order_return_get_serials(request) -> list[str]:
    return request.session.get(ORDER_RETURN_SERIALS_KEY, [])


def order_return_save_serials(request, serials: list[str]) -> None:
    request.session[ORDER_RETURN_SERIALS_KEY] = serials
    request.session.modified = True


def order_return_dedup_upper(values) -> list[str]:
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
    serials = order_return_get_serials(request)

    if request.method == 'POST':
        posted_serial = (request.POST.get('serial') or '').strip().upper()

        if 'add_serial' in request.POST:
            if not posted_serial:
                messages.info(request, "Digite um serial.")
            else:
                serials = order_return_get_serials(request)
                if posted_serial not in serials:
                    serials.append(posted_serial)
                    order_return_save_serials(request, serials)
                    messages.success(request, "Serial inserido.")
                else:
                    messages.warning(request, "Serial já está na lista.")
            form = OrderReturnCheckForm(request.POST or None,
                                        name_form="Conferir Volume de Retirada")
            return render(request, 'logistica/order_return_check.html', {
                'form': form,
                'name_form': "Conferir Volume de Retirada",
                'site_title': "Conferir Volume de Retirada",
                'botao_texto': "Conferir",
                'serials': order_return_get_serials(request),
            })

        if 'remove_serial' in request.POST:
            try:
                idx = int(request.POST.get('remove_serial'))
                serials = order_return_get_serials(request)
                if 0 <= idx < len(serials):
                    removido = serials.pop(idx)
                    order_return_save_serials(request, serials)
                    messages.success(request, f"Removido: {removido}")
            except Exception:
                messages.error(request, "Não foi possível remover o serial.")
            return render(request, 'logistica/order_return_check.html', {
                'form': form,
                'name_form': "Conferir Volume de Retirada",
                'site_title': "Conferir Volume de Retirada",
                'botao_texto': "Conferir",
                'serials': order_return_get_serials(request),
            })

        if 'clear_serials' in request.POST:
            order_return_save_serials(request, [])
            messages.success(request, "Lista de seriais limpa.")
            form = OrderReturnCheckForm(request.POST or None,
                                        name_form="Conferir Volume de Retirada")
            return render(request, 'logistica/order_return_check.html', {
                'form': form,
                'name_form': "Conferir Volume de Retirada",
                'site_title': "Conferir Volume de Retirada",
                'botao_texto': "Conferir",
                'serials': order_return_get_serials(request),
            })
        form = OrderReturnCheckForm(request.POST or None,
                                    name_form="Conferir Volume de Retirada")
        if form.is_valid():
            serials = order_return_save_serials(request)
            serials = order_return_dedup_upper(serials)

            if not serials:
                unico = (form.cleaned_data.get('serial') or '').strip().upper()
                if not unico:
                    messages.warning(
                        request, "Adicione ao menos um serial antes de enviar.")
                    return render(request, 'logistica/order_return_check.html', {
                        'form': form,
                        'name_form': "Conferir Volume de Retirada",
                        'site_title': "Conferir Volume de Retirada",
                        'botao_texto': "Conferir",
                        'serials': order_return_get_serials(request),
                    })
                serials = [unico]
        messages.error(
            request, f"Corrija os erros do formulário: {form.errors.as_text()}")
        return render(request, 'logistica/order_return_check.html', {
            'form': form,
            'name_form': "Conferir Volume de Retirada",
            'site_title': "Conferir Volume de Retirada",
            'botao_texto': "Conferir",
            'serials': order_return_get_serials(request),
        })

    initial = {}
    if _consume_carry_next(request):
        initial['serial'] = ''

    form = OrderReturnCheckForm(request.POST or None,
                                name_form="Conferir Volume de Retirada")
    return render(request, 'logistica/order_return_check.html', {
        'form': form,
        'name_form': "Conferir Volume de Retirada",
        'site_title': "Conferir Volume de Retirada",
        'botao_texto': "Conferir",
    })
