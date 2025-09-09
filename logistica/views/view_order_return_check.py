from ..forms import OrderReturnCheckForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from setup.local_settings import API_URL
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

CARRY_PEDIDO_KEY = "carry_pedido_next"

JSON_CT = "application/json"


def _mark_carry_next(request):
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True


def _consume_carry_next(request) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


RESERVA_SERIALS_KEY = "reserva_serials"


def reserva_get_serials(request) -> list[str]:
    return request.session.get(RESERVA_SERIALS_KEY, [])


def reserva_save_serials(request, serials: list[str]) -> None:
    request.session[RESERVA_SERIALS_KEY] = serials
    request.session.modified = True


def reserva_dedup_upper(values) -> list[str]:
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

    if request.method != 'POST':

        pedido = (request.GET.get('order')
                  or request.session.get('order') or '').strip()

        if pedido:
            request.session['order'] = pedido
            request.session.modified = True

        initial = {'order': pedido}
        if _consume_carry_next(request):
            initial['serial'] = ''

        form = OrderReturnCheckForm(
            name_form="Conferir Volume de Retirada", initial=initial)
        return render(request, 'logistica/order_return_check.html', {
            'form': form,
            'botao_texto': 'Enviar',
            'site_title': "Conferir Volume de Retirada",
            'serials': reserva_get_serials(request),
            'show_serial': True,
        })

    serials = reserva_get_serials(request)

    posted_pedido = (request.POST.get('order') or '').strip()
    if posted_pedido:
        request.session['order'] = posted_pedido
        request.session.modified = True

    posted_serial = (request.POST.get('serial') or '').strip().upper()

    if 'add_serial' in request.POST:
        if not posted_serial:
            messages.info(request, "Digite um serial.")
        else:
            serials = reserva_get_serials(request)
            if posted_serial not in serials:
                serials.append(posted_serial)
                reserva_save_serials(request, serials)
                messages.success(request, "Serial inserido.")
            else:
                messages.warning(request, "Serial já está na lista.")
        _mark_carry_next(request)
        return redirect(request.path)

    if 'remove_serial' in request.POST:
        try:
            idx = int(request.POST.get("remove_serial"))
            serials = reserva_get_serials(request)
            if 0 <= idx < len(serials):
                removido = serials.pop(idx)
                reserva_save_serials(request, serials)
                messages.success(request, f"Removido: {removido}")
        except Exception:
            messages.error(request, "Não foi possível remover o serial.")
        _mark_carry_next(request)
        return redirect(request.path)

    if 'clear_serials' in request.POST:
        reserva_save_serials(request, [])
        messages.success(request, "Lista de seriais limpa.")
        _mark_carry_next(request)
        return redirect(request.path)

    form = OrderReturnCheckForm(
        request.POST, name_form="Conferir Volume de Retirada")
    if form.is_valid():
        serials = reserva_dedup_upper(reserva_get_serials(request))
        if not serials:
            unico = (form.cleaned_data.get('serial') or '').strip().upper()
            if not unico:
                messages.warning(
                    request, "Adicione ao menos 1 serial antes de enviar.")
                return redirect(request.path)
            serials = [unico]
            reserva_save_serials(request, serials)

        pedido = (request.session.get('order') or '').strip()
        if not pedido:
            messages.error(request, "Pedido não informado.")
            return redirect(request.path)

        url = f"{API_URL}/api/v2/trackings/send"
        payload = {
            "order_number": pedido,
            "volume_number": 1,
            "order_type": "RETURN",
            "tracking_code": "210",
            "bar_codes": serials,
            "to_location_id": 11
        }

        client = RequestClient(
            url=url,
            method="POST",
            headers={"Accept": JSON_CT},
            request_data=payload
        )
        print(payload)
        print(serials)
        result = client.send_api_request()

        if isinstance(result, dict) and result.get('detail'):
            messages.error(request, f"{result['detail']}")
        else:
            messages.success(request, "Conferência enviada com sucesso.")

        _mark_carry_next(request)
        return redirect(request.path)

    messages.warning(
        request, f"Corrija os erros do formulário: {form.errors.as_text()}")
    return redirect(request.path)
