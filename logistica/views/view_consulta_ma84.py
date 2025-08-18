from ..forms import ConsultaResultMA84Form
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages


def buscar_dados(tp_reg, serial):
    url = f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ma/{tp_reg}?serge={serial}',
    request_api = RequestClient(
        headers={'Content-Type': 'application/json'},
        method='get',
        url=url[0],
    )
    response = request_api.send_api_request()
    return [response]


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def consulta_ma84(request):
    id_pre_recebido = request.session.get('id_pre_recebido')
    serial_inserido = request.session.get('serial_recebido')
    origem = request.session.get('origem')
    mostrar_tabela = request.session.get('mostrar_tabela', False)

    tp_reg = (
        request.POST.get('tp_reg') or
        request.GET.get('tp_reg') or
        request.session.get('tp_reg', '')
    )

    if request.method == 'POST':
        form = ConsultaResultMA84Form(request.POST)

        if form.data.get('tp_reg') in ('84', '85') and form.data.get('serial') == '':
            form.add_error(
                'serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/consulta_result_ma.html', {
                'form': form,
                'tabela_dados': None,
                'etapa_ativa': 'consulta_result_ma',
                'tp_reg': form.data.get('tp_reg', '')
            })

        if form.is_valid():
            novo_tp_reg = form.cleaned_data['tp_reg']
            serial = form.cleaned_data.get('serial', '')

            request.session['tp_reg'] = novo_tp_reg
            request.session['id_pre_recebido'] = form.cleaned_data.get(
                'id', '')
            request.session['serial_recebido'] = serial
            request.session['origem'] = 'consulta_result'
            request.session['mostrar_tabela'] = True

            return redirect('logistica:consulta_result_ma')

    else:
        initial_data = {}

        if id_pre_recebido:
            initial_data['id'] = id_pre_recebido

        if origem == 'pre-recebimento':
            initial_data['tp_reg'] = '84'
        elif origem == 'estorno_result':
            dados_estorno = request.session.get('dados_estorno', {})
            initial_data.update(dados_estorno)

        form = ConsultaResultMA84Form(initial=initial_data)

    try:
        dados = buscar_dados(
            tp_reg, serial_inserido) if mostrar_tabela else None
    except Exception:
        messages.error(request, "Erro ao enviar requisição")
        dados = None

    return render(request, 'logistica/consulta_result_ma.html', {
        'form': form,
        'tabela_dados': dados,
        'etapa_ativa': 'consulta_result_ma',
        'tp_reg': tp_reg,
        'botao_texto': 'Consultar',
        'site_title': 'SAP - Consulta Resultados MA'
    })


@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
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
