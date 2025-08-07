from ..forms import ConsultaResultMA84Form
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

def buscar_dados(tp_reg,serial):

    request_api = RequestClient(
                headers={'Content-Type': 'application/json'},
                method='get',
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ma/{tp_reg}/?serge={serial}',
            )
    response = request_api.send_api_request()
    
    return [
        response
    ]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def consulta_ma84(request, tp_reg: str):
    id_pre_recebido = request.session.pop('id_pre_recebido', None)
    serial_inserido = request.session.pop('serial_recebido', None)
    origem = request.session.pop('origem', None)
    mostrar_tabela = request.session.pop('mostrar_tabela', False)

    if request.method == 'POST':
        form = ConsultaResultMA84Form(request.POST)

        if form.data.get('tp_reg') in ('84', '85') and form.data.get('serial') == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/consulta_result_ma.html', {'form': form})

        if form.is_valid():
            novo_tp_reg = form.cleaned_data['tp_reg']
            request.session['id_pre_recebido'] = form.cleaned_data.get('id', '')
            request.session['serial_recebido'] = form.cleaned_data.get('serial', '')
            request.session['origem'] = 'consulta_result'
            request.session['mostrar_tabela'] = True

            return redirect('logistica:consulta_result_ma', tp_reg=novo_tp_reg)

    else:
        initial_data = {'tp_reg': tp_reg}
        if id_pre_recebido:
            initial_data['id'] = id_pre_recebido
        if origem == 'pre-recebimento':
            initial_data['tp_reg'] = '84'
        elif origem == 'estorno_result':
            dados_estorno = request.session.pop('dados_estorno', {})
            initial_data.update(dados_estorno)

        form = ConsultaResultMA84Form(initial=initial_data)

    dados = buscar_dados(form) if mostrar_tabela else None

    return render(request, 'logistica/consulta_result_ma.html', {
        'form': form,
        'tabela_dados': dados,
        'etapa_ativa': 'consulta_result_ma',
        'tp_reg': tp_reg,
    })

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def btn_ma_voltar(request, tp_reg):
    id_valor = request.POST.get('id') or request.GET.get('id')
    print(tp_reg)
    if tp_reg == '84':
        return redirect('logistica:consulta_result_ma', tp_reg=tp_reg)
    elif tp_reg == '85':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:estorno_reserva')
    else:
        return redirect('logistica:consulta_result_ma', tp_reg=tp_reg)