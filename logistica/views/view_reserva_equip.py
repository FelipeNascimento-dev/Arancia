from ..forms import ReservaEquipamentosForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def reserva_equip(request, tp_reg):
    titulo = 'Reserva de Equipamento' if tp_reg == '84' else 'Estorno Reserva de Equipamento'
    if request.method == 'POST':
        form = ReservaEquipamentosForm(request.POST, nome_form=titulo)
        if form.is_valid():
            centro = form.cleaned_data.get('centro')
            deposito = form.cleaned_data.get('deposito')
            serial = form.cleaned_data.get('serial')

            request.session['serge'] = serial
            request.session['centro'] = centro
            request.session['deposito'] = deposito

            request_client = RequestClient(
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ma/{tp_reg}',
                method='POST',
                headers={'Content-Type': 'application/json'},
                request_data={
                    "serge": serial,
                    "centro": centro,
                    "deposito": deposito
                }
            )
            request_client.send_api_request()

            return redirect('logistica:consulta_result_ma')
    else:
        form = ReservaEquipamentosForm(nome_form=titulo)
    
    return render(request, 'logistica/reserva_equip.html', {
        'form': form,
        'etapa_ativa': 'reserva',
        'botao_texto': 'Enviar',
        })