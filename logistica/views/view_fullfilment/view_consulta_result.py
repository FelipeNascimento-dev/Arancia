from ...forms.forms_fullfilment.forms_consulta_result import ConsultaPreRecebimentoForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required


def buscar_dados(request, tp_reg, id_pre_recebido, serial_inserido):

    request_api = RequestClient(
        headers={'Content-Type': 'application/json'},
        method='get',
        url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/mo/{tp_reg}/?id_lote={id_pre_recebido}&serge={serial_inserido}',
    )
    response = request_api.send_api_request()

    return [
        response
    ]


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.entrada_flfm', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def consulta_result(request):
    id_pre_recebido = request.session.get('id_pre_recebido')
    serial_inserido = request.session.get('serial_recebido')
    origem = request.session.get('origem')
    mostrar_tabela = request.session.get('mostrar_tabela', False)

    if request.method == 'POST':
        form = ConsultaPreRecebimentoForm(request.POST)

        if form.data.get('tp_reg') in ('15', '16') and form.data.get('serial') == '':
            form.add_error(
                'serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/consulta_result.html', {
                'form': form,
                'tabela_dados': None,
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

            return redirect('logistica:consulta_resultados')

    else:
        initial_data = {}
        tp_reg = request.session.get('tp_reg', '')

        if id_pre_recebido:
            initial_data['id'] = id_pre_recebido

        if origem == 'pre-recebimento':
            initial_data['tp_reg'] = '13'
        elif origem == 'recebimento':
            initial_data['tp_reg'] = '15'
            initial_data['serial'] = serial_inserido
        elif origem == 'estorno_result':
            dados_estorno = request.session.get('dados_estorno', {})
            initial_data.update(dados_estorno)

        form = ConsultaPreRecebimentoForm(initial=initial_data)

    try:
        dados = buscar_dados(request, tp_reg, id_pre_recebido,
                             serial_inserido) if mostrar_tabela else None
    except Exception as e:
        messages.error(request, "Erro ao enviar requisição")
        dados = None

    return render(request, 'logistica/consulta_result.html', {
        'form': form,
        'tabela_dados': dados,
        'tp_reg': tp_reg,
        'botao_texto': 'Consultar',
        'site_title': 'SAP - Consulta Resultados',
    })


@login_required(login_url='logistica:login')
@permission_required('logistica.entrada_flfm', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def btn_voltar(request):
    tp_reg = (
        request.POST.get('tp_reg') or
        request.GET.get('tp_reg') or
        request.session.get('tp_reg')
    )
    id_valor = request.POST.get('id') or request.GET.get('id')

    if tp_reg == '13':
        return redirect('logistica:pre_recebimento', tp_reg=tp_reg)
    elif tp_reg == '15':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:recebimento', tp_reg=tp_reg)
    elif tp_reg == '14':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:estorno_recebimento', tp_reg=tp_reg)
    elif tp_reg == '16':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:estorno_pre_recebimento', tp_reg=tp_reg)
    else:
        return redirect('logistica:consulta_resultados')
