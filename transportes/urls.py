from django.urls import path
from .views import extrair_enderecos_view, gerar_etiquetas_view, painel_tecnicos_view,dashboard_view



app_name = 'transportes'

urlpatterns = [

    path('painel-de-gerenciamento/',dashboard_view, name='painel'),
    path("gerar-etiquetas/", gerar_etiquetas_view, name="gerar_etiquetas"),
    path("extrair-enderecos/", extrair_enderecos_view, name="extrair_enderecos"),
    path("painel-tecnicos/", painel_tecnicos_view, name="painel_tecnicos"),
]
