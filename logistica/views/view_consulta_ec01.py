from ..forms import ConsultaResultEC01Form
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

CARRY_PEDIDO_KEY = "carry_pedido_next"

def _mark_carry_next(request):
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True

def _consume_carry_next(request) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)

def buscar_dados(tp_reg: str, serial: str):
    tp_reg_new = str(tp_reg).zfill(2)
    request_api = RequestClient(
        headers={'Content-Type': 'application/json'},
        method='get',
        url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ec/{tp_reg_new}/{serial}',
    )
    response = request_api.send_api_request()
    return [response]


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def consulta_ec01(request):
    id_pre_recebido = request.session.pop('id_pre_recebido', None)
    serial = request.session.pop('serial', None)
    origem = request.session.pop('origem', None)
    mostrar_tabela = request.session.pop('mostrar_tabela', False)

    initial_data = {}

    if request.method == 'POST':
        form = ConsultaResultEC01Form(request.POST)

        posted_gtec = (request.POST.get('gtec') or '').strip()
        if posted_gtec:
            request.session['pedido'] = posted_gtec
            request.session.modified = True

        if form.data.get('tp_reg') in ('1', '2') and (form.data.get('serial') or '').strip() == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/consulta_result_ec.html', {
                'form': form,
                'tabela_dados': None,
                'etapa_ativa': 'consulta_result_ec',
                'tp_reg': form.data.get('tp_reg', ''),
                'botao_texto': 'Consultar',
                'site_title': 'SAP - Consulta Resultados EC',
            })

        if form.is_valid():
            tp_reg = form.cleaned_data.get('tp_reg')
            serial = form.cleaned_data.get('serial', '') or ''

            request.session['tp_reg'] = tp_reg
            request.session['id_pre_recebido'] = form.cleaned_data.get('id', '')
            request.session['serial_recebido'] = serial
            request.session['origem'] = 'consulta_result'
            mostrar_tabela = True
            request.session['mostrar_tabela'] = True

            dados = buscar_dados(tp_reg, serial) if mostrar_tabela else None

            return render(request, 'logistica/consulta_result_ec.html', {
                'form': form,
                'tabela_dados': dados,
                'etapa_ativa': 'consulta_result_ec',
                'tp_reg': tp_reg,
                'botao_texto': 'Consultar',
                'site_title': 'SAP - Consulta Resultados EC',
            })

        messages.warning(request, 'Corrija os erros do formulário.')
        return render(request, 'logistica/consulta_result_ec.html', {
            'form': form,
            'tabela_dados': None,
            'etapa_ativa': 'consulta_result_ec',
            'tp_reg': form.data.get('tp_reg', ''),
            'botao_texto': 'Consultar',
            'site_title': 'SAP - Consulta Resultados EC',
        })

    if id_pre_recebido:
        initial_data['id'] = id_pre_recebido

    if origem == 'pre-recebimento':
        initial_data['tp_reg'] = '1'
    elif origem == 'estorno_result':
        dados_estorno = request.session.pop('dados_estorno', {})
        initial_data.update(dados_estorno)

    if _consume_carry_next(request):
        ped = (request.session.get('pedido') or '').strip()
        if ped:
            initial_data['gtec'] = ped

    form = ConsultaResultEC01Form(initial=initial_data)

    return render(request, 'logistica/consulta_result_ec.html', {
        'form': form,
        'tabela_dados': None,
        'etapa_ativa': 'consulta_result_ec',
        'tp_reg': initial_data.get('tp_reg', ''),
        'botao_texto': 'Consultar',
        'site_title': 'SAP - Consulta Resultados EC',
    })


@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def btn_ec_voltar(request, tp_reg):
    id_valor = request.POST.get('id') or request.GET.get('id')
    if tp_reg == '01':
        return redirect('logistica:consulta_result_ec', tp_reg=tp_reg)
    elif tp_reg == '02':
        return redirect('logistica:estorno_saida_campo')
    else:
        return redirect('logistica:consulta_result_ec', tp_reg=tp_reg)
