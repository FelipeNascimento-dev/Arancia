import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from ..forms import trackingIPForm
from utils.request import RequestClient
from setup.local_settings import DEBUG

SESSION_PREFIX = "retorno_serials_"

class TrackingOriginalCode:
    def __init__(self, code: str):
        self.original_code = code
        self.show_serial = False
        self.etapa_ativa = None
        if code == '200':
            self.description = 'Recebido para picking'
        elif code == '201':
            self.description = 'PCP'
            self.etapa_ativa = 'pcp'
        elif code == '202':
            self.description = 'Retorno do picking'
            self.etapa_ativa = 'retorno_picking'
            self.show_serial = True
        elif code == '203':
            self.description = 'Consolidação'
            self.etapa_ativa = 'consolidacao'
        elif code == '204':
            self.description = 'Expedição'
            self.etapa_ativa = 'expedicao'
        elif code == '205':
            self.description = 'Troca de custodia'
            self.etapa_ativa = 'troca_custodia'

def _session_key(pedido: str | None) -> str:
    return f"{SESSION_PREFIX}{pedido or 'tmp'}"

def _build_initial(form_obj, request, pedido_atual: str | None, exclude=('serial',)):
    initial = {}
    for name in getattr(form_obj, 'fields', {}):
        if name in exclude:
            continue
        val = request.POST.get(name, None)
        if val not in (None, ''):
            initial[name] = val

    if 'pedido' in getattr(form_obj, 'fields', {}) and not initial.get('pedido'):
        if pedido_atual:
            initial['pedido'] = pedido_atual
        elif request.session.get('pedido'):
            initial['pedido'] = request.session['pedido']

    return initial

def trackingIP(request, code):
    code_info = TrackingOriginalCode(code)
    titulo = f'IP - {code_info.description}'

    pedido_atual = request.POST.get('pedido') or request.session.get('pedido')
    key = _session_key(pedido_atual) if code == '202' else None
    serials = request.session.get(key, []) if key else []

    if request.method == 'POST':
        form = trackingIPForm(request.POST, nome_form=titulo, show_serial=code_info.show_serial)

        if code == '202':
            if pedido_atual and request.session.get('pedido') != pedido_atual:
                request.session['pedido'] = pedido_atual
                key = _session_key(pedido_atual)
                serials = request.session.get(key, [])

            if 'add_serial' in request.POST:
                s = (request.POST.get('serial') or '').strip().upper()
                if not pedido_atual:
                    messages.error(request, 'Informe o número do pedido antes de inserir seriais.')
                elif not s:
                    messages.info(request, 'Digite um serial.')
                else:
                    if s not in serials:
                        serials.append(s)
                        messages.success(request, 'Serial inserido.')
                    else:
                        messages.info(request, 'Serial já está na lista.')
                    request.session[key] = serials
                    request.session.modified = True

                if pedido_atual:
                    request.session['pedido'] = pedido_atual

                initial = _build_initial(form, request, pedido_atual, exclude=('serial',))
                form = trackingIPForm(initial=initial, nome_form=titulo, show_serial=code_info.show_serial)

                return render(request, "logistica/pcp.html", {
                    "form": form,
                    "etapa_ativa": code_info.etapa_ativa,
                    "botao_texto": "Enviar",
                    "serials": serials,
                    "show_serial": code_info.show_serial,
                })

            if 'remove_serial' in request.POST:
                try:
                    idx = int(request.POST.get('remove_serial'))
                    if 0 <= idx < len(serials):
                        removido = serials.pop(idx)
                        messages.success(request, f"Removido: {removido}")
                        request.session[key] = serials
                        request.session.modified = True
                except Exception:
                    messages.error(request, "Não foi possível remover o serial.")

                initial = _build_initial(form, request, pedido_atual, exclude=())
                form = trackingIPForm(initial=initial, nome_form=titulo, show_serial=code_info.show_serial)

                return render(request, "logistica/pcp.html", {
                    "form": form,
                    "etapa_ativa": code_info.etapa_ativa,
                    "botao_texto": "Enviar",
                    "serials": serials,
                    "show_serial": code_info.show_serial,
                })

            if 'clear_serials' in request.POST:
                request.session[key] = []
                request.session.modified = True
                messages.success(request, "Lista de seriais limpa.")

                initial = _build_initial(form, request, pedido_atual, exclude=('serial',))
                form = trackingIPForm(initial=initial, nome_form=titulo, show_serial=code_info.show_serial)

                return render(request, "logistica/pcp.html", {
                    "form": form,
                    "etapa_ativa": code_info.etapa_ativa,
                    "botao_texto": "Enviar",
                    "serials": [],
                    "show_serial": code_info.show_serial,
                })
            
        if 'enviar_evento' in request.POST:
            if form.is_valid():
                numero_pedido = str(form.cleaned_data.get('pedido'))
                request.session['pedido'] = numero_pedido

                request_data = {
                    "shipper": "C-Trends",
                    "shipper_federal_tax_id": "20056828000179",
                    "order_number": numero_pedido,
                    "volume_number": 1,
                    "events": [
                        {
                            "event_date": datetime.datetime.now().astimezone().isoformat(),
                            "original_code": code_info.original_code,
                            "original_message": code_info.description,
                        }
                    ]
                }

                request_client = RequestClient(
                    url='http://192.168.0.216/homo-fulfillment/api/order-sumary/add-tracking',
                    method='POST',
                    headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                    request_data=request_data
                )

                try:
                    resp = request_client.send_api_request()
                    ok = getattr(resp, "ok", False)
                    status = getattr(resp, "status_code", 0) or 0
                    if ok or (200 <= int(status) < 300):
                        messages.success(request, f'A mensagem "{code_info.description}" foi enviada com sucesso!')

                        if code == '202':
                            request.session[_session_key(numero_pedido)] = []
                            request.session.modified = True
                        if code == '201':
                            return redirect('logistica:reserva_equip', tp_reg=84)
                        elif code == '203':
                            return redirect('logistica:saida_campo', tp_reg=1)
                        elif code == '204':
                            return redirect('logistica:pcp', code=201)
                        else:
                            prox = int(code) + 1
                            return redirect('logistica:pcp', code=prox)
                    else:
                        messages.error(request, f'Falha ao enviar rastreamento (status {status}).')
                except Exception as e:
                    if DEBUG:
                        messages.error(request, f'{e}')
                    else:
                        messages.error(request, 'Erro ao enviar requisição!')
            else:
                messages.error(request, f"Corrija os erros do formulário: {form.errors.as_text()}")

        return render(request, "logistica/pcp.html", {
            "form": form,
            "etapa_ativa": code_info.etapa_ativa,
            "botao_texto": "Enviar",
            "serials": serials if code == '202' else [],
            "show_serial": code_info.show_serial,
        })

    form = trackingIPForm(nome_form=titulo, show_serial=code_info.show_serial)
    return render(request, "logistica/pcp.html", {
        "form": form,
        "etapa_ativa": code_info.etapa_ativa,
        "botao_texto": "Enviar",
        "serials": serials if code == '202' else [],
        "show_serial": code_info.show_serial,
    })