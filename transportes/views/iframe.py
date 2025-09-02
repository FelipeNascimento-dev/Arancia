from django.urls import path
from django.shortcuts import render

# Views simples que apenas rendem um template com iframe
def gerar_etiquetas_view(request):
    return render(request, "transportes/controle_campo/iframe.html", {
        "titulo": "Gerar Etiquetas",
        "url": "https://gerador-qr-code-1y1k.onrender.com"
    })

def extrair_enderecos_view(request):
    return render(request, "transportes/controle_campo/iframe.html", {
        "titulo": "Extrair Endereços",
        "url": "http://192.168.0.221:8002"
    })

def painel_tecnicos_view(request):
    return render(request, "transportes/controle_campo/iframe.html", {
        "titulo": "Painel de Técnicos",
        "url": "http://192.168.0.221:8000"
    })