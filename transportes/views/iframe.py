from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect

# Views simples que apenas rendem um template com iframe


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.gerar_etiquetas', raise_exception=True)
def gerar_etiquetas_view(request):
    return render(request, "transportes/controle_campo/frame2.html", {
        "titulo": "Gerar Etiquetas",
        "url": "https://5cab688efce1.ngrok-free.app"
    })


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def extrair_enderecos_view(request):
    return render(request, "transportes/controle_campo/frame2.html", {
        "titulo": "Extrair Endereços",
        "current_parent_menu": "transportes",
        "current_menu": "controle_campo",
        "current_submenu": "endereco",
        "url": "http://192.168.0.221:8002"
    })


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def painel_Dashboard_view(request):
    return render(request, "transportes/controle_campo/iframe.html", {
        "titulo": "Dashboard",
        "current_parent_menu": "transportes",
        "current_menu": "controle_campo",
        "current_submenu": "painel",
        "current_subsubmenu": "dashboard",
        "url": "http://192.168.0.221:8501/"
    })
