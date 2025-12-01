from ...forms import ConsultaResultMA84Form
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

CARRY_PEDIDO_KEY = "carry_pedido_next"


def _consume_carry_next(request) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


def buscar_dados(tp_reg: str, serial: str):
    tp_reg_new = str(tp_reg).strip().zfill(2)
    url = f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ma/{tp_reg_new}?serge={serial}'
    request_api = RequestClient(
        headers={'Content-Type': 'application/json'},
        method='get',
        url=url,
    )
    response = request_api.send_api_request()
    return [response]


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def consulta_ma84(request):
    id_pre_recebido = request.session.get('id_pre_recebido')
    serial_inserido = request.session.get('serial_recebido', '')
    origem = request.session.get('origem')
    tp_reg_session = request.session.get('tp_reg', '')

    dados = None
    tp_reg = request.POST.get('tp_reg') or request.GET.get(
        'tp_reg') or tp_reg_session

    if request.method == 'POST':
        posted_pedido = (request.POST.get('pedido') or '').strip()
        if posted_pedido:
            request.session['pedido'] = posted_pedido
            request.session.modified = True

        form = ConsultaResultMA84Form(request.POST)

        if form.data.get('tp_reg') in ('84', '85') and not (form.data.get('serial') or '').strip():
            form.add_error(
                'serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/consulta_result_ma.html', {
                'form': form,
                'tabela_dados': None,
                'etapa_ativa': 'consulta_result_ma',
                'tp_reg': form.data.get('tp_reg', ''),
                'botao_texto': 'Consultar',
                'site_title': 'SAP - Consulta Resultados MA',
            })

        if form.is_valid():
            novo_tp_reg = form.cleaned_data['tp_reg']
            serial = (form.cleaned_data.get('serial') or '').strip()

            request.session['tp_reg'] = novo_tp_reg
            request.session['id_pre_recebido'] = form.cleaned_data.get(
                'id', '')
            request.session['serial_recebido'] = serial
            request.session['origem'] = 'consulta_result'

            try:
                dados_resp = buscar_dados(novo_tp_reg, serial) if (
                    novo_tp_reg and serial) else None
                dados = dados_resp if dados_resp else None

                if dados and isinstance(dados, list):
                    first = dados[0]
                    if isinstance(first, dict) and 'detail' in first:
                        messages.error(request, first['detail'])
                elif isinstance(dados, dict) and 'detail' in dados:
                    messages.error(request, dados['detail'])

            except Exception:
                messages.error(request, "Erro ao enviar requisição")
                dados = None

            return render(request, 'logistica/consulta_result_ma.html', {
                'form': form,
                'tabela_dados': dados,
                'etapa_ativa': 'consulta_result_ma',
                'tp_reg': novo_tp_reg,
                'botao_texto': 'Consultar',
                'site_title': 'SAP - Consulta Resultados MA',
            })

        return render(request, 'logistica/consulta_result_ma.html', {
            'form': form,
            'tabela_dados': None,
            'etapa_ativa': 'consulta_result_ma',
            'tp_reg': form.data.get('tp_reg', ''),
            'botao_texto': 'Consultar',
            'site_title': 'SAP - Consulta Resultados MA',
        })

    # GET
    initial_data = {}
    pedido_session = (request.session.get('pedido') or '').strip()
    if pedido_session:
        initial_data['pedido'] = pedido_session

    if id_pre_recebido:
        initial_data['id'] = id_pre_recebido

    if origem == 'pre-recebimento':
        initial_data['tp_reg'] = '84'
    elif origem == 'estorno_result':
        dados_estorno = request.session.get('dados_estorno', {})
        initial_data.update(dados_estorno)

    if 'tp_reg' not in initial_data and tp_reg:
        initial_data['tp_reg'] = tp_reg

    form = ConsultaResultMA84Form(initial=initial_data)

    return render(request, 'logistica/consulta_result_ma.html', {
        'form': form,
        'tabela_dados': None,
        'etapa_ativa': 'consulta_result_ma',
        'tp_reg': initial_data.get('tp_reg', tp_reg),
        'botao_texto': 'Consultar',
        'site_title': 'SAP - Consulta Resultados MA',
    })


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def btn_ma_voltar(request):
    tp_reg = (
        request.POST.get('tp_reg') or
        request.GET.get('tp_reg') or
        request.session.get('tp_reg')
    )
    id_valor = request.POST.get('id') or request.GET.get('id')

    if tp_reg == '84':
        return redirect('logistica:consulta_result_ma')
    elif tp_reg == '85':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:estorno_reserva')
    else:
        return redirect('logistica:consulta_result_ma')
