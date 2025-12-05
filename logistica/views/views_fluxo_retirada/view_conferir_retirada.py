from ...forms import OrderReturnCheckForm
from utils.request import RequestClient
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from setup.local_settings import API_URL
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import STOCK_API_URL
import json
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


SERIAL_CHIP_MAP = "serial_chip_map"


def reserva_get_chip_map(request) -> dict:
    return request.session.get(SERIAL_CHIP_MAP, {})


def reserva_save_chip_map(request, data: dict):
    request.session[SERIAL_CHIP_MAP] = data
    request.session.modified = True


SERIAL_MODEL_MAP = "serial_model_map"


def reserva_get_serial_map(request) -> dict:
    return request.session.get(SERIAL_MODEL_MAP, {})


def reserva_save_serial_map(request, data: dict):
    request.session[SERIAL_MODEL_MAP] = data
    request.session.modified = True


def reserva_get_product_map(request):
    return request.session.get("product_map", {})


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
@permission_required('logistica.acesso_arancia', raise_exception=True)
def order_return_check(request):
    user: User = request.user
    if request.method != 'POST':
        pedido = request.session.get('order')

        if pedido:
            request.session['order'] = pedido
            request.session.modified = True

        initial = {'order': pedido}
        if _consume_carry_next(request):
            initial['serial'] = ''

        form = OrderReturnCheckForm(
            name_form="Conferir Volume de Retirada", initial=initial)
        return render(request, 'logistica/templates_fluxo_retirada/conferir_retirada.html', {
            'form': form,
            'botao_texto': 'Enviar',
            'site_title': "Conferir Volume de Retirada",
            'serials': reserva_get_serials(request),
            'serial_model_map': reserva_get_serial_map(request),
            'product_map': reserva_get_product_map(request),
            'chip_map': reserva_get_chip_map(request),
            'show_serial': True,
        })

    serials = reserva_get_serials(request)

    posted_pedido = (request.POST.get('order') or '').strip()
    if posted_pedido:
        request.session['order'] = posted_pedido
        request.session.modified = True

    posted_serial = (request.POST.get('serial') or '').strip().upper()

    if 'add_serial' in request.POST:
        show_modal = False
        modal_serial = None

        if not posted_serial:
            messages.info(request, "Digite um serial.")
        else:
            serials = reserva_get_serials(request)

            if posted_serial not in serials:
                serials.append(posted_serial)
                reserva_save_serials(request, serials)
                messages.success(request, "Serial inserido.")

                show_modal = True
                modal_serial = posted_serial
            else:
                messages.warning(request, "Serial já está na lista.")

        _mark_carry_next(request)

        form = OrderReturnCheckForm(
            name_form="Conferir Volume de Retirada",
            initial={'order': request.session.get('order'), 'serial': ''}
        )

        product_choices = []
        product_map = {}

        client_name = user.username

        try:
            if client_name:
                url_products = f"{STOCK_API_URL}/v1/products/cielo"
                res = RequestClient(
                    url=url_products,
                    method="GET",
                    headers={"Accept": "application/json"}
                )
                result = res.send_api_request()

                try:
                    if isinstance(result, (dict, list)):
                        data = result
                    elif isinstance(result, (str, bytes)):
                        data = json.loads(result)
                    elif hasattr(result, "json"):
                        data = result.json()
                    elif hasattr(result, "text"):
                        data = json.loads(result.text)
                    else:
                        data = []
                except Exception:
                    data = []

                if isinstance(data, list) and len(data) > 0:
                    for p in data:
                        product_id = str(p.get("id") or "")
                        sku = p.get("sku") or p.get("product_code") or ""
                        desc = p.get("description") or p.get(
                            "product_name") or "Sem descrição"
                        display_name = f"{sku} - {desc}".strip(" -")

                        product_choices.append((product_id, display_name))
                        product_map[product_id] = {
                            "sku": sku,
                            "desc": desc,
                            "id": product_id,
                        }

                    request.session["product_map"] = product_map
                else:
                    product_choices = [("", "Nenhum produto encontrado")]
            else:
                product_choices = [("", "Cliente não selecionado")]

        except Exception as e:
            messages.error(request, f"Erro ao obter produtos: {e}")
            product_choices = [("", "Erro ao carregar produtos")]

        return render(request, "logistica/templates_fluxo_retirada/conferir_retirada.html", {
            'form': form,
            'botao_texto': 'Enviar',
            'site_title': "Conferir Volume de Retirada",
            'serials': reserva_get_serials(request),
            'chip_map': reserva_get_chip_map(request),
            'show_serial': True,
            "show_modal": show_modal,
            "modal_serial": modal_serial,
            "product_choices": product_choices,

        })

    if 'remove_serial' in request.POST:
        try:
            idx = int(request.POST.get("remove_serial"))
            serials = reserva_get_serials(request)
            serial_to_remove = serials[idx]

            serials.pop(idx)
            reserva_save_serials(request, serials)

            serial_map = reserva_get_serial_map(request)
            serial_map.pop(serial_to_remove, None)
            reserva_save_serial_map(request, serial_map)

            messages.success(request, f"Removido: {serial_to_remove}")
        except Exception:
            messages.error(request, "Não foi possível remover o serial.")

    if request.POST.get("save_model"):
        serial = request.POST.get("serial", "").strip().upper()
        product_id = request.POST.get("product_id", "").strip()
        chip_number = request.POST.get("chip_number", "").strip()

        if not serial or not product_id or not chip_number:
            messages.error(
                request, "Selecione um modelo e informe o chip number.")
            return redirect(request.path)

        serial_map = reserva_get_serial_map(request)
        serial_map[serial] = int(product_id)
        reserva_save_serial_map(request, serial_map)

        chip_map = reserva_get_chip_map(request)
        chip_map[serial] = chip_number
        reserva_save_chip_map(request, chip_map)

        messages.success(
            request, f"Modelo e chip associados ao serial {serial}.")
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
        try:
            location_id = (user.designacao.informacao_adicional.id
                           if user.designacao and user.designacao.informacao_adicional
                           else None)
        except Exception as e:
            location_id = None
            print(f"Erro ao obter location_id do user {user}: {e}")
            messages.error(
                request, f"Erro ao obter location_id do user {user}: {e}")
            return redirect(request.path)

        url = f"{API_URL}/api/v2/trackings/send"
        payload = {
            "order_number": pedido,
            "volume_number": 1,
            "order_type": "RETURN",
            "tracking_code": "210",
            "bar_codes": [
                {
                    "serial_number": s,
                    "product_id": reserva_get_serial_map(request).get(s),
                    "chip_number": reserva_get_chip_map(request).get(s)
                }
                for s in serials
            ],
            "to_location_id": location_id,
            "from_location_id": location_id,
            "created_by": user.username
        }
        print(payload)
        client = RequestClient(
            url=url,
            method="POST",
            headers={"Accept": JSON_CT},
            request_data=payload
        )
        result = client.send_api_request()

    if isinstance(result, dict) and result.get('detail'):
        messages.error(request, f"{result['detail']}")
        _mark_carry_next(request)
        return redirect(request.path)
    else:
        messages.success(request, "Conferência enviada com sucesso.")

        reserva_save_serials(request, [])
        request.session.pop('order', None)
        request.session.pop(CARRY_PEDIDO_KEY, None)
        request.session.pop(SERIAL_MODEL_MAP, None)
        request.session.modified = True

        return redirect('logistica:order_return_check')
