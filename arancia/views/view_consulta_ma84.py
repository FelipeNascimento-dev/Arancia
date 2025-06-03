from ..forms import ConsultaResultMA84Form
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect


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
def consulta_ma84(request, tp_reg: str):
    id_pre_recebido = request.session.pop('id_pre_recebido', None)
    serial_inserido = request.session.pop('serial_recebido', None)
    origem = request.session.pop('origem', None)
    mostrar_tabela = request.session.pop('mostrar_tabela', False)

    if request.method == 'POST':
        form = ConsultaResultMA84Form(request.POST)

        if form.data.get('tp_reg') in ('84', '85') and form.data.get('serial') == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'arancia/consulta_result_ma.html', {'form': form})

        if form.is_valid():
            novo_tp_reg = form.cleaned_data['tp_reg']
            request.session['id_pre_recebido'] = form.cleaned_data.get('id', '')
            request.session['serial_recebido'] = form.cleaned_data.get('serial', '')
            request.session['origem'] = 'consulta_result'
            request.session['mostrar_tabela'] = True

            return redirect('arancia:consulta_result_ma', tp_reg=novo_tp_reg)

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

    return render(request, 'arancia/consulta_result_ma.html', {
        'form': form,
        'tabela_dados': dados,
        'tp_reg': tp_reg,
    })

def btn_ma_voltar(request, tp_reg):
    id_valor = request.POST.get('id') or request.GET.get('id')
    print(tp_reg)
    if tp_reg == '84':
        return redirect('arancia:consulta_result_ma', tp_reg=tp_reg)
    elif tp_reg == '85':
        if id_valor:
            request.session['id_pre_recebido'] = id_valor
        return redirect('arancia:estorno_reserva')
    else:
        return redirect('arancia:consulta_result_ma', tp_reg=tp_reg)