from ...forms import SaidaCampoForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import STOCK_API_URL

SAIDA_SERIALS_KEY = "saida_serials"
SAIDA_CHIP_MAP_KEY = "saida_chip_map"
SAIDA_CHIP_REQUIRED_KEY = "saida_chip_required"

CARRY_PEDIDO_KEY = "carry_pedido_next"


def _mark_carry_next(request):
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True


def _consume_carry_next(request) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


def saida_get_serials(request) -> list[str]:
    return request.session.get(SAIDA_SERIALS_KEY, [])


def saida_save_serials(request, serials: list[str]) -> None:
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
@permission_required('logistica.acesso_arancia', raise_exception=True)
def saida_campo(request, tp_reg: str):
    titulo = (
        'SAP - Saida para Campo' if str(tp_reg) == '1'
        else 'SAP - Cancelamento de Saida para Campo'
    )
    tp_reg_new = str(tp_reg).zfill(2)

    serials = saida_get_serials(request)

    if request.method == 'POST':
        posted_serial = (request.POST.get('serial') or '').strip().upper()

        gtec_post = request.POST.get('gtec')
        origem_os_post = request.POST.get('origem_os')
        initial = {'gtec': gtec_post, 'origem_os': origem_os_post}

        posted_gtec = (request.POST.get('gtec') or '').strip()
        if posted_gtec:
            request.session['pedido'] = posted_gtec
            request.session.modified = True

        if request.POST.get('cancel_chip'):
            serial = (request.POST.get('serial') or '').strip().upper()

            serials = saida_get_serials(request)
            if serial in serials:
                serials.remove(serial)
                saida_save_serials(request, serials)

            chip_map = request.session.get(SAIDA_CHIP_MAP_KEY, {})
            chip_map.pop(serial, None)
            request.session[SAIDA_CHIP_MAP_KEY] = chip_map

            required = request.session.get(SAIDA_CHIP_REQUIRED_KEY, [])
            if serial in required:
                required.remove(serial)
            request.session[SAIDA_CHIP_REQUIRED_KEY] = required
            request.session.modified = True

            messages.warning(
                request,
                f"Serial {serial} descartado. É obrigatório informar o chip."
            )
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': saida_get_serials(request),
                'show_serial': True,
                'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                "current_parent_menu": "logistica",
                "current_menu": "SAP",
                "current_submenu": "sap_saida",
                "current_subsubmenu": "saida_campo"
            })

        if request.POST.get('save_chip'):
            serial = (request.POST.get('serial') or '').strip().upper()
            chip_number = (request.POST.get('chip_number') or '').strip()

            if not chip_number:
                serials = saida_get_serials(request)
                if serial in serials:
                    serials.remove(serial)
                    saida_save_serials(request, serials)

                required = request.session.get(SAIDA_CHIP_REQUIRED_KEY, [])
                if serial in required:
                    required.remove(serial)
                request.session[SAIDA_CHIP_REQUIRED_KEY] = required
                request.session.modified = True

                messages.error(
                    request,
                    f"O chip é obrigatório. O serial {serial} não foi inserido."
                )
                form = SaidaCampoForm(nome_form=titulo, initial=initial)
                return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                    'form': form,
                    'etapa_ativa': 'saida_campo',
                    'botao_texto': 'Enviar',
                    'site_title': titulo,
                    'serials': saida_get_serials(request),
                    'show_serial': True,
                    'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                    "current_parent_menu": "logistica",
                    "current_menu": "SAP",
                    "current_submenu": "sap_saida",
                    "current_subsubmenu": "saida_campo"
                })

            chip_map = request.session.get(SAIDA_CHIP_MAP_KEY, {})

            chip_ja_usado = next(
                (s for s, c in chip_map.items()
                 if c == chip_number and s != serial),
                None
            )

            if chip_ja_usado:
                messages.error(
                    request,
                    f"O chip {chip_number} já está associado ao serial {chip_ja_usado}. "
                    "Não é permitido usar o mesmo chip em dois seriais diferentes."
                )

                serials = saida_get_serials(request)
                if serial in serials:
                    serials.remove(serial)
                    saida_save_serials(request, serials)

                required = request.session.get(SAIDA_CHIP_REQUIRED_KEY, [])
                if serial in required:
                    required.remove(serial)
                request.session[SAIDA_CHIP_REQUIRED_KEY] = required
                request.session.modified = True

                form = SaidaCampoForm(nome_form=titulo, initial=initial)
                return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                    'form': form,
                    'etapa_ativa': 'saida_campo',
                    'botao_texto': 'Enviar',
                    'site_title': titulo,
                    'serials': saida_get_serials(request),
                    'show_serial': True,
                    'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                    "current_parent_menu": "logistica",
                    "current_menu": "SAP",
                    "current_submenu": "sap_saida",
                    "current_subsubmenu": "saida_campo"
                })

            chip_map[serial] = chip_number
            request.session[SAIDA_CHIP_MAP_KEY] = chip_map
            request.session.modified = True

            messages.success(
                request, f"Chip {chip_number} associado ao serial {serial}."
            )
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': saida_get_serials(request),
                'show_serial': True,
                'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                "current_parent_menu": "logistica",
                "current_menu": "SAP",
                "current_submenu": "sap_saida",
                "current_subsubmenu": "saida_campo"
            })

        if 'add_serial' in request.POST:
            show_modal = False
            modal_serial = None
            modal_chip = ""

            if not posted_serial:
                messages.info(request, "Digite um serial.")
            else:
                serials = saida_get_serials(request)
                if posted_serial not in serials:
                    user = request.user
                    sales_channel = user.designacao.informacao_adicional.sales_channel
                    if sales_channel == 'all':
                        location_id = 0
                    else:
                        location_id = user.designacao.informacao_adicional_id

                    url = (
                        f"{STOCK_API_URL}/v1/items/delivery/{posted_serial}"
                        f"?client=cielo&location_id={location_id}"
                    )
                    api_client = RequestClient(
                        url=url,
                        method="GET",
                        headers={"accept": "application/json"}
                    )
                    resp_api = api_client.send_api_request()

                    if not isinstance(resp_api, dict):
                        messages.error(request, "Erro ao consultar o serial na PA.")
                    elif 'detail' in resp_api:
                        messages.error(request, resp_api.get('detail'))
                    else:
                        serials.append(posted_serial)
                        saida_save_serials(request, serials)
                        messages.success(request, "Serial inserido.")

                        if resp_api.get("required_chip") is True:
                            required = request.session.get(SAIDA_CHIP_REQUIRED_KEY, [])
                            if posted_serial not in required:
                                required.append(posted_serial)
                            request.session[SAIDA_CHIP_REQUIRED_KEY] = required
                            request.session.modified = True

                            show_modal = True
                            modal_serial = posted_serial

                            chip_serial = resp_api.get("chip_serial")
                            if chip_serial and chip_serial != "None":
                                chip_map = request.session.get(SAIDA_CHIP_MAP_KEY, {})
                                chip_map[posted_serial] = chip_serial
                                request.session[SAIDA_CHIP_MAP_KEY] = chip_map
                                request.session.modified = True
                                modal_chip = chip_serial
                else:
                    messages.warning(request, "Serial já está na lista.")
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': saida_get_serials(request),
                'show_serial': True,
                'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                'show_modal': show_modal,
                'modal_serial': modal_serial,
                'modal_chip': modal_chip,
                "current_parent_menu": "logistica",
                "current_menu": "SAP",
                "current_submenu": "sap_saida",
                "current_subsubmenu": "saida_campo"
            })

        if 'remove_serial' in request.POST:
            try:
                idx = int(request.POST.get("remove_serial"))
                serials = saida_get_serials(request)
                if 0 <= idx < len(serials):
                    removido = serials.pop(idx)
                    saida_save_serials(request, serials)

                    chip_map = request.session.get(SAIDA_CHIP_MAP_KEY, {})
                    chip_map.pop(removido, None)
                    request.session[SAIDA_CHIP_MAP_KEY] = chip_map

                    required = request.session.get(SAIDA_CHIP_REQUIRED_KEY, [])
                    if removido in required:
                        required.remove(removido)
                    request.session[SAIDA_CHIP_REQUIRED_KEY] = required
                    request.session.modified = True

                    messages.success(request, f"Removido: {removido}")
            except Exception:
                messages.error(request, "Não foi possível remover o serial.")
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': saida_get_serials(request),
                'show_serial': True,
                'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                "current_parent_menu": "logistica",
                "current_menu": "SAP",
                "current_submenu": "sap_saida",
                "current_subsubmenu": "saida_campo"
            })

        if 'clear_serials' in request.POST:
            saida_save_serials(request, [])
            request.session[SAIDA_CHIP_MAP_KEY] = {}
            request.session[SAIDA_CHIP_REQUIRED_KEY] = []
            request.session.modified = True
            messages.success(request, "Lista de seriais limpa.")
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': [],
                'show_serial': True,
                'chip_map': {},
                "current_parent_menu": "logistica",
                "current_menu": "SAP",
                "current_submenu": "sap_saida",
                "current_subsubmenu": "saida_campo"
            })

        form = SaidaCampoForm(request.POST, nome_form=titulo)
        if form.is_valid():
            gtec = form.cleaned_data.get('gtec')
            origem_os = form.cleaned_data.get('origem_os')

            serials = saida_get_serials(request)
            serials = saida_dedup_upper(serials)

            if not serials:
                unico = (form.cleaned_data.get('serial') or '').strip().upper()
                if not unico:
                    messages.warning(
                        request, "Adicione ao menos 1 serial antes de enviar.")
                    return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                        'form': form,
                        'etapa_ativa': 'saida_campo',
                        'botao_texto': 'Enviar',
                        'site_title': titulo,
                        'serials': saida_get_serials(request),
                        'show_serial': True,
                        'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                        "current_parent_menu": "logistica",
                        "current_menu": "SAP",
                        "current_submenu": "sap_saida",
                        "current_subsubmenu": "saida_campo"
                    })
                serials = [unico]

            chip_map = request.session.get(SAIDA_CHIP_MAP_KEY, {})
            required = request.session.get(SAIDA_CHIP_REQUIRED_KEY, [])
            pendentes = [
                s for s in serials if s in required and not chip_map.get(s)
            ]
            if pendentes:
                messages.warning(
                    request,
                    f"Informe o chip dos seriais: {', '.join(pendentes)}")
                return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                    'form': form,
                    'etapa_ativa': 'saida_campo',
                    'botao_texto': 'Enviar',
                    'site_title': titulo,
                    'serials': saida_get_serials(request),
                    'show_serial': True,
                    'chip_map': chip_map,
                    "current_parent_menu": "logistica",
                    "current_menu": "SAP",
                    "current_submenu": "sap_saida",
                    "current_subsubmenu": "saida_campo"
                })

            request.session['serials_ec'] = serials
            request.session['gtec'] = gtec
            request.session['origem_os'] = origem_os

            user = request.user
            deposito = (
                user.designacao.informacao_adicional.deposito
                if user.designacao and user.designacao.informacao_adicional
                else None
            )
            cod_centro = (
                user.designacao.informacao_adicional.cod_center
                if user.designacao and user.designacao.informacao_adicional
                else None
            )

            usuarios_com_lock_ip_false = {"ARC0050", "ARC0007"}

            username = getattr(request.user, "username", "")
            query = "?lock_ip=false" if username in usuarios_com_lock_ip_false else ""

            request_client = RequestClient(
                url=(
                    f"http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ec/"
                    f"{tp_reg_new}/list{query}"
                ),
                method='POST',
                headers={'Content-Type': 'application/json'},
                request_data={
                    "serges": serials,
                    "znum_gt": gtec,
                    "centro": cod_centro,
                    "deposito": deposito,
                    "bktxt": "0",
                    "origem_os": origem_os,
                    "chipnumber": chip_map,
                }
            )

            try:
                resp = request_client.send_api_request()

                if 'detail' in resp:
                    messages.error(request, resp.get('detail'))
                else:
                    messages.success(request, 'Requisição enviada com sucesso')
            except Exception as e:
                messages.error(request, f"Erro ao enviar requisição: {e}")
                return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
                    'form': SaidaCampoForm(
                        nome_form=titulo,
                        initial={'gtec': gtec, 'origem_os': origem_os}
                    ),
                    'etapa_ativa': 'saida_campo',
                    'botao_texto': 'Enviar',
                    'site_title': titulo,
                    'serials': saida_get_serials(request),
                    'show_serial': True,
                    'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
                    "current_parent_menu": "logistica",
                    "current_menu": "SAP",
                    "current_submenu": "sap_saida",
                    "current_subsubmenu": "saida_campo"
                })

            saida_save_serials(request, [])
            request.session[SAIDA_CHIP_MAP_KEY] = {}
            request.session[SAIDA_CHIP_REQUIRED_KEY] = []
            request.session.modified = True
            _mark_carry_next(request)
            return redirect('logistica:consulta_result_ec')

        messages.error(
            request, f"Corrija os erros do formulário: {form.errors.as_text()}")
        return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
            'form': form,
            'etapa_ativa': 'saida_campo',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': saida_get_serials(request),
            'show_serial': True,
            'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
            "current_parent_menu": "logistica",
            "current_menu": "SAP",
            "current_submenu": "sap_saida",
            "current_subsubmenu": "saida_campo"
        })

    initial = {}
    if _consume_carry_next(request):
        ped = (request.session.get('pedido') or '').strip()
        if ped:
            initial['gtec'] = ped

    form = SaidaCampoForm(nome_form=titulo, initial=initial)
    return render(request, 'logistica/templates_fluxo_entrega/saida_campo.html', {
        'form': form,
        'etapa_ativa': 'saida_campo',
        'botao_texto': 'Enviar',
        'site_title': titulo,
        'serials': saida_get_serials(request),
        'show_serial': True,
        'chip_map': request.session.get(SAIDA_CHIP_MAP_KEY, {}),
        "current_parent_menu": "logistica",
        "current_menu": "SAP",
        "current_submenu": "sap_saida",
        "current_subsubmenu": "saida_campo"
    })
