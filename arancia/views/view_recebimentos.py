from django.shortcuts import render, redirect
from ..forms import PreRecebimentoForm, RecebimentoForm
from utils.request import RequestClient


def pre_recebimento(request):
    if request.method == 'POST':
        form = PreRecebimentoForm(request.POST)
        if form.is_valid():
            # Obtendo os dados do formulário
            id_inserido = form.cleaned_data.get('id')
            qtde_vol_inserida = form.cleaned_data.get('qtde_vol')
            centro_origem_inserido = form.cleaned_data.get(
                'centro_origem')
            deposito_origem_inserido = form.cleaned_data.get('deposito_origem')
            centro_destino_inserido = form.cleaned_data.get('centro_destino')
            deposito_destino_inserido = form.cleaned_data.get(
                'deposito_destino')

            # Armazenando os dados na sessão
            request.session['id_pre_recebido'] = id_inserido
            request.session['origem'] = 'pre-recebimento'

            # Enviando os dados para a API
            request_client = RequestClient(
                url='http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/mo/13',
                method='POST',
                headers={'Content-Type': 'application/json'},
                request_data={
                    "id_lote": id_inserido,
                    "nr_controle_transp": "1234",
                    "qtde_vol": qtde_vol_inserida,
                    "centro_origem": centro_origem_inserido,
                    "deposito_origem": deposito_origem_inserido,
                    "centro_destino": centro_destino_inserido,
                    "deposito_destino": deposito_destino_inserido
                }
            )
            result = request_client.send_api_request()
            if result.get('status_code') != 200:
                # Se a requisição falhar, exibe uma mensagem de erro
                form.add_error(
                    None, 'Atenção: {}'.format(result.get('detail')))
                return render(request, 'arancia/pre_recebimento.html', {'form': form})

            return redirect('arancia:consulta_resultados', tp_reg='13')
    else:
        form = PreRecebimentoForm()

    return render(request, 'arancia/pre_recebimento.html', {'form': form})


def recebimento(request):
    if request.method == 'POST':
        form = RecebimentoForm(request.POST)
        if form.is_valid():
            id_inserido = form.cleaned_data.get('id')
            serial_inserido = form.cleaned_data.get('serial')
            request.session['id_pre_recebido'] = id_inserido
            request.session['origem'] = 'recebimento'
            request.session['serial_recebido'] = serial_inserido
            return redirect('arancia:consulta_resultados', tp_reg='15')
    else:
        id_inserido = request.session.get('id_pre_recebido')
        initial_data = {'id': id_inserido} if id_inserido else {}
        form = RecebimentoForm(initial=initial_data)

    return render(request, 'arancia/recebimento.html', {'form': form})
