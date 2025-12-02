from ...forms import ReservaEquipamentosForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

CARRY_PEDIDO_KEY = "carry_pedido_next"


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
@permission_required('logistica.acesso_arancia', raise_exception=True)
def reserva_equip(request, tp_reg):
    titulo = 'SAP - Reserva de Equipamento' if str(
        tp_reg) == '84' else 'SAP - Estorno Reserva de Equipamento'

    if request.method != 'POST':
        initial = {}
        if _consume_carry_next(request):
            ped = (request.session.get('pedido') or '').strip()
            if ped:
                initial['pedido'] = ped
        form = ReservaEquipamentosForm(nome_form=titulo, initial=initial)
        return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
            'form': form,
            'etapa_ativa': 'reserva',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': reserva_get_serials(request),
            'show_serial': True,
        })

    serials = reserva_get_serials(request)

    posted_pedido = (request.POST.get('pedido') or '').strip()
    if posted_pedido:
        request.session['pedido'] = posted_pedido
        request.session.modified = True

    initial = {}
    if posted_pedido:
        initial['pedido'] = posted_pedido
    else:
        sess_ped = (request.session.get('pedido') or '').strip()
        if sess_ped:
            initial['pedido'] = sess_ped

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
        form = ReservaEquipamentosForm(nome_form=titulo, initial=initial)
        return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
            'form': form,
            'etapa_ativa': 'reserva',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': reserva_get_serials(request),
            'show_serial': True,
        })

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
        form = ReservaEquipamentosForm(nome_form=titulo, initial=initial)
        return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
            'form': form,
            'etapa_ativa': 'reserva',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': reserva_get_serials(request),
            'show_serial': True,
        })

    if 'clear_serials' in request.POST:
        reserva_save_serials(request, [])
        messages.success(request, "Lista de seriais limpa.")
        form = ReservaEquipamentosForm(nome_form=titulo, initial=initial)
        return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
            'form': form,
            'etapa_ativa': 'reserva',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': [],
            'show_serial': True,
        })

    form = ReservaEquipamentosForm(request.POST, nome_form=titulo)
    if form.is_valid():
        serials = reserva_dedup_upper(reserva_get_serials(request))
        if not serials:
            unico = (form.cleaned_data.get('serial') or '').strip().upper()
            if not unico:
                messages.warning(
                    request, "Adicione ao menos 1 serial antes de enviar.")
                return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
                    'form': form,
                    'etapa_ativa': 'reserva',
                    'botao_texto': 'Enviar',
                    'site_title': titulo,
                    'serials': reserva_get_serials(request),
                    'show_serial': True,
                })
            serials = [unico]

        user = request.user
        deposito = (
            user.designacao.informacao_adicional.deposito
            if user.designacao and user.designacao.informacao_adicional
            else None
        )
        cod_centro = (
            user.designacao.informacao_adicional.cod_certer
            if user.designacao and user.designacao.informacao_adicional
            else None
        )
        request_client = RequestClient(
            url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ma/{tp_reg}/list',
            method='POST',
            headers={'Content-Type': 'application/json'},
            request_data={
                "serges": serials,
                "centro": cod_centro,
                "deposito": deposito
            }
        )

        try:
            request_client.send_api_request()

            messages.success(
                request, f"{len(serials)} serial(is) enviado(s) com sucesso.")
            reserva_save_serials(request, [])
            _mark_carry_next(request)
            return redirect('logistica:consulta_result_ma')

        except Exception as e:
            messages.error(request, f"Erro ao enviar requisição: {e}")

        return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
            'form': form,
            'etapa_ativa': 'reserva',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': reserva_get_serials(request),
            'show_serial': True,
        })
    else:
        messages.warning(
            request, f"Corrija os erros do formulário: {form.errors.as_text()}")
        return render(request, 'logistica/templates_fluxo_entrega/reserva_equip.html', {
            'form': form,
            'etapa_ativa': 'reserva',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': reserva_get_serials(request),
            'show_serial': True,
        })
