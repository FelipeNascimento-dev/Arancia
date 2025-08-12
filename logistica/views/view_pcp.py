import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from ..forms import trackingIPForm
from utils.request import RequestClient
from setup.local_settings import DEBUG

class TrackingOriginalCode:
    def __init__(self, code:str):
        self.original_code = code
        self.show_serial = False
        self.etapa_ativa = None
        if code == '200':
            self.description = 'Recebido para picking'
        elif code == '201':
            self.description = 'PCP'
            self.etapa_ativa = 'pcp'
        elif code == '202':
            self.description = 'Retorno do picking'
            self.etapa_ativa = 'retorno_picking'
            self.show_serial = True
        elif code == '203':
            self.description = 'Consolidação'
            self.etapa_ativa = 'consolidacao'
        elif code == '204':
            self.description = 'Expedição'
            self.etapa_ativa = 'expedicao'
        elif code == '205':
            self.description = 'Troca de custodia'
            self.etapa_ativa = 'troca_custodia'

def trackingIP(request, code):
    code_info = TrackingOriginalCode(code)
        
    titulo = f'IP - {code_info.description}' 

    if request.method == 'POST':
        form = trackingIPForm(request.POST, nome_form=titulo, show_serial=code_info.show_serial)

        if form.is_valid():
            numero_pedido = str(form.cleaned_data.get('pedido'))
            request.session['pedido'] = numero_pedido
       
        request_data={
                    "shipper": "C-Trends",
                    "shipper_federal_tax_id": "20056828000179",
                    "order_number": numero_pedido,
                    "volume_number": 1,
                    "events": [
                        {
                        "event_date": datetime.datetime.now().astimezone().isoformat(),
                        "original_code": code_info.original_code,
                        "original_message": code_info.description
                        }
                    ]
                    }  

        print(request_data)
        request_client = RequestClient(
            url=f'http://192.168.0.216/homo-fulfillment/api/order-sumary/add-tracking',
            method='POST',
            headers={'Content-Type': 'application/json'},
            request_data=request_data)
        
        try:
            request_client.send_api_request()
            messages.sucess(request, f'A mensagem "{code_info.description}" foi enviada com sucesso!')
            if code == 201:
                return redirect 
        except Exception as e:
            print(e)
            if DEBUG:
                messages.error(request, e)
            else: 
                messages.error(request, 'Erro ao enviar requisição!')
            return render(request, "logistica/pcp.html", {
            "form": form,
            "etapa_ativa": code_info.etapa_ativa,
            'botao_texto': 'Enviar',
        })
        
    
    else:
        form = trackingIPForm(nome_form=titulo, show_serial=code_info.show_serial)

    return render(request, "logistica/pcp.html", {
        "form": form,
        "etapa_ativa": code_info.etapa_ativa,
        'botao_texto': 'Enviar',
    })