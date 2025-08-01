from ..forms.forms_consulta_result import ConsultaPreRecebimentoForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def buscar_dados(form):
    return [
        {
            'nr_arq': '123456',
            'mensagem': 'sem erro',
            'status': 'Enviado',
            'data': '01/01/2025',
            'hora': '12:00:00',
        }
    ]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def consulta_result(request, tp_reg: str):
    id_pre_recebido = request.session.pop('id_pre_recebido', None)
    serial_inserido = request.session.pop('serial_recebido', None)
    origem = request.session.pop('origem', None)
    mostrar_tabela = request.session.pop('mostrar_tabela', False)

    if request.method == 'POST':
        form = ConsultaPreRecebimentoForm(request.POST)

        if form.data.get('tp_reg') in ('15', '16') and form.data.get('serial') == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/consulta_result.html', {'form': form})

        if form.is_valid():
            novo_tp_reg = form.cleaned_data['tp_reg']
            request.session['id_pre_recebido'] = form.cleaned_data.get('id', '')
            request.session['serial_recebido'] = form.cleaned_data.get('serial', '')
            request.session['origem'] = 'consulta_result'
            request.session['mostrar_tabela'] = True

            return redirect('logistica:consulta_resultados', tp_reg=novo_tp_reg)

    else:
        initial_data = {'tp_reg': tp_reg}
        if id_pre_recebido:
            initial_data['id'] = id_pre_recebido
        if origem == 'pre-recebimento':
            initial_data['tp_reg'] = '13'
        elif origem == 'recebimento':
            initial_data['tp_reg'] = '15'
            initial_data['serial'] = serial_inserido
        elif origem == 'estorno_result':
            dados_estorno = request.session.pop('dados_estorno', {})
            initial_data.update(dados_estorno)

        form = ConsultaPreRecebimentoForm(initial=initial_data)

    dados = buscar_dados(form) if mostrar_tabela else None

    return render(request, 'logistica/consulta_result.html', {
        'form': form,
        'tabela_dados': dados,
        'tp_reg': tp_reg,
    })

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def btn_voltar(request, tp_reg):
    id_valor = request.POST.get('id') or request.GET.get('id')
    if tp_reg == '13':
        return redirect('logistica:pre_recebimento')
    elif tp_reg == '15':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:recebimento')
    elif tp_reg in ('14', '16'):
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('logistica:estorno')
    else:
        return redirect('logistica:consulta_resultados', tp_reg=tp_reg)