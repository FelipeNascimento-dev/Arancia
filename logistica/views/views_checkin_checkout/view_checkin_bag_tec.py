from django.shortcuts import render, redirect
from ...forms import CheckInBagTecForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
import json

@login_required(login_url='logistica:login')
@permission_required('logistica.checkin_principal', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def checkin_bag_tec(request):
    titulo = "Check-In de Bag Tec"
    form = CheckInBagTecForm(request.POST or None, nome_form=titulo)
    return render(
        request,
        "logistica/templates_checkin_checkout/checkin_bag_tec.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Confirmar Check-In",
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "checkin_bag_tec",
        },
    )