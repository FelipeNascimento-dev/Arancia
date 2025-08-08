from ..forms import SaidaCampoForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def saida_campo(request, tp_reg:str):
    titulo = 'Saida para Campo' if tp_reg == '1' else 'Cancelamento de Saida para Campo'
    tp_reg_new = tp_reg.zfill(2)
    if request.method == 'POST':
        form = SaidaCampoForm(request.POST, nome_form=titulo)
        if form.is_valid():
            serial = form.cleaned_data.get('serial')
            gtec = form.cleaned_data.get('gtec')
            centro = form.cleaned_data.get('centro')
            deposito = form.cleaned_data.get('deposito')
            origem_os = form.cleaned_data.get('origem_os')

            request.session['serial'] = serial
            request.session['gtec'] = gtec
            request.session['centro'] = centro
            request.session['deposito'] = deposito
            request.session['origem_os'] = origem_os

            request_client = RequestClient(
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/ec/{tp_reg_new}',
                method='POST',
                headers={'Content-Type': 'application/json'},
                request_data={
                    "serge": serial,
                    "znum_gt": gtec,
                    "centro": centro,
                    "deposito": deposito,
                    "bktxt": "0",
                    "origem_os": origem_os,
                }
            )
            try:
                request_client.send_api_request()
            except Exception as e:
                messages.error(request, "Erro ao enviar requisição")
                return render(request, 'logistica/saida_campo.html', {
                    'form': form,
                    'etapa_ativa': 'saida_campo',
                })

            return redirect('logistica:consulta_result_ec', tp_reg=tp_reg)
    else:
        form = SaidaCampoForm(nome_form=titulo)
    
    return render(request, 'logistica/saida_campo.html', {
        'form': form,
        'etapa_ativa': 'saida_campo',
        'botao_texto': 'Enviar',
        })
