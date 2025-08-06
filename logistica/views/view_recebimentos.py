from django.shortcuts import render, redirect
from ..forms import PreRecebimentoForm, RecebimentoForm
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required

def enviar_para_api(tp_reg, payload):
    request_client = RequestClient(
        url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/mo/{tp_reg}',
        method='POST',
        headers={'Content-Type': 'application/json'},
        request_data=payload
    )
    request_client.send_api_request()

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def pre_recebimento(request, tp_reg):
    titulo = 'Pré-Recebimento' if tp_reg == '13' else 'Estorno de Pré-Recebimento'
    if request.method == 'POST':
        form = PreRecebimentoForm(request.POST, nome_form=titulo)
        if form.is_valid():
            id_inserido = form.cleaned_data.get('id')
            payload = {
                "id_lote": id_inserido,
                "nr_controle_transp": id_inserido,
                "qtde_vol": form.cleaned_data.get('qtde_vol'),
                "centro_origem": form.cleaned_data.get('centro_origem'),
                "deposito_origem": form.cleaned_data.get('deposito_origem'),
                "centro_destino": form.cleaned_data.get('centro_destino'),
                "deposito_destino": form.cleaned_data.get('deposito_destino'),
            }

            request.session['id_pre_recebido'] = id_inserido
            request.session['origem'] = 'pre-recebimento'

            enviar_para_api(tp_reg, payload)
            return redirect('logistica:consulta_resultados', tp_reg=tp_reg)
    else:
        form = PreRecebimentoForm(nome_form=titulo)

    return render(request, 'logistica/pre_recebimento.html', {'form': form})

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def recebimento(request, tp_reg):
    titulo = 'Recebimento' if tp_reg == '15' else 'Estorno de Recebimento'
    if request.method == 'POST':

        form = RecebimentoForm(request.POST, nome_form=titulo)
        if form.is_valid():
            id_inserido = form.cleaned_data.get('id')
            serial_inserido = form.cleaned_data.get('serial')

            request.session['id_pre_recebido'] = id_inserido
            request.session['origem'] = 'recebimento'
            request.session['serial_recebido'] = serial_inserido

            return redirect('logistica:consulta_resultados', tp_reg=tp_reg)
    else:
        id_inserido = request.session.get('id_pre_recebido')
        initial_data = {'id': id_inserido} if id_inserido else {}
        form = RecebimentoForm(initial=initial_data, nome_form=titulo)

    return render(request, 'logistica/recebimento.html', {'form': form})