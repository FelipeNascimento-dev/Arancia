from ..forms import SaidaCampoForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

SAIDA_SERIALS_KEY = "saida_serials"

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
def saida_campo(request, tp_reg: str):
    titulo = 'SAP - Saida para Campo' if str(tp_reg) == '1' else 'SAP - Cancelamento de Saida para Campo'
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

        if 'add_serial' in request.POST:
            if not posted_serial:
                messages.info(request, "Digite um serial.")
            else:
                serials = saida_get_serials(request)
                if posted_serial not in serials:
                    serials.append(posted_serial)
                    saida_save_serials(request, serials)
                    messages.success(request, "Serial inserido.")
                else:
                    messages.warning(request, "Serial já está na lista.")
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': saida_get_serials(request),
                'show_serial': True,
            })

        if 'remove_serial' in request.POST:
            try:
                idx = int(request.POST.get("remove_serial"))
                serials = saida_get_serials(request)
                if 0 <= idx < len(serials):
                    removido = serials.pop(idx)
                    saida_save_serials(request, serials)
                    messages.success(request, f"Removido: {removido}")
            except Exception:
                messages.error(request, "Não foi possível remover o serial.")
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': saida_get_serials(request),
                'show_serial': True,
            })

        if 'clear_serials' in request.POST:
            saida_save_serials(request, [])
            messages.success(request, "Lista de seriais limpa.")
            form = SaidaCampoForm(nome_form=titulo, initial=initial)
            return render(request, 'logistica/saida_campo.html', {
                'form': form,
                'etapa_ativa': 'saida_campo',
                'botao_texto': 'Enviar',
                'site_title': titulo,
                'serials': [],
                'show_serial': True,
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
                    messages.warning(request, "Adicione ao menos 1 serial antes de enviar.")
                    return render(request, 'logistica/saida_campo.html', {
                        'form': form,
                        'etapa_ativa': 'saida_campo',
                        'botao_texto': 'Enviar',
                        'site_title': titulo,
                        'serials': saida_get_serials(request),
                        'show_serial': True,
                    })
                serials = [unico]

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
            request_client = RequestClient(
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ec/{tp_reg_new}/list',
                method='POST',
                headers={'Content-Type': 'application/json'},
                request_data={
                    "serges": serials,
                    "znum_gt": gtec,
                    "centro": cod_centro,
                    "deposito": deposito,
                    "bktxt": "0",
                    "origem_os": origem_os,
                }
            )
            try:
                resp=request_client.send_api_request() 
                if not isinstance(resp, list):
                    if isinstance(resp, dict) and resp.get("detail"):
                        raise Exception(resp)
                messages.success(request,'Mensagem enviada com sucesso')
            except Exception as e:
                messages.error(request, f"Erro ao enviar requisição: {e}")
                return render(request, 'logistica/saida_campo.html', {
                    'form': SaidaCampoForm(nome_form=titulo, initial={'gtec': gtec, 'origem_os': origem_os}),
                    'etapa_ativa': 'saida_campo',
                    'botao_texto': 'Enviar',
                    'site_title': titulo,
                    'serials': saida_get_serials(request),
                    'show_serial': True,
                })

            saida_save_serials(request, [])
            _mark_carry_next(request)
            return redirect('logistica:consulta_result_ec')

        messages.error(request, f"Corrija os erros do formulário: {form.errors.as_text()}")
        return render(request, 'logistica/saida_campo.html', {
            'form': form,
            'etapa_ativa': 'saida_campo',
            'botao_texto': 'Enviar',
            'site_title': titulo,
            'serials': saida_get_serials(request),
            'show_serial': True,
        })

    initial = {}
    if _consume_carry_next(request):
        ped = (request.session.get('pedido') or '').strip()
        if ped:
            initial['gtec'] = ped

    form = SaidaCampoForm(nome_form=titulo, initial=initial)
    return render(request, 'logistica/saida_campo.html', {
        'form': form,
        'etapa_ativa': 'saida_campo',
        'botao_texto': 'Enviar',
        'site_title': titulo,
        'serials': saida_get_serials(request),
        'show_serial': True,
    })