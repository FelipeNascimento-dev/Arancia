import datetime
from typing import Iterable, Tuple, Optional

from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from ..forms import trackingIPForm
from utils.request import RequestClient
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import API_URL

#####  TRACKING CODIGOS PARA RETORNO DO PICKING #####


class TrackingOriginalCode:
    def __init__(self, code: str):
        self.original_code = code
        self.show_serial = False
        self.etapa_ativa: Optional[str] = None

        if code == "200":
            self.description = "Recebido para picking"
        elif code == "201":
            self.description = "PCP"
            self.etapa_ativa = "pcp"
        elif code == "202":
            self.description = "Retorno do picking"
            self.etapa_ativa = "retorno_picking"
            self.show_serial = True
        elif code == "203":
            self.description = "Consolidação"
            self.etapa_ativa = "consolidacao"
        elif code == "204":
            self.description = "Expedição"
            self.etapa_ativa = "expedicao"
        elif code == "205":
            self.description = "Troca de custodia"
            self.etapa_ativa = "troca_custodia"
        else:
            self.description = "Etapa desconhecida"

###### view principal tracking IP #####


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def trackingIP(request: HttpRequest, code: str) -> HttpResponse:
