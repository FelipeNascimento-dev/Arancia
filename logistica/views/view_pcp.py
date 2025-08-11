from django.shortcuts import render
from django.http import HttpResponse
from ..forms import trackingIPForm

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
            self.description = 'Troca de custódia'
            self.etapa_ativa = 'troca_custodia'
        


def trackingIP(request, code):
    code_info = TrackingOriginalCode(code)
        
    titulo = f'IP - {code_info.description}' 
    form = trackingIPForm(request.POST or None, nome_form=titulo, show_serial=code_info.show_serial)

    return render(request, "logistica/pcp.html", {
        "form": form,
        "etapa_ativa": code_info.etapa_ativa,
        'botao_texto': 'Enviar',
    })