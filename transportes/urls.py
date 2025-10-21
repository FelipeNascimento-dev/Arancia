from django.urls import path

from transportes.views.View_session import config_context_view
from transportes.views.iframe import painel_Dashboard_view
from transportes.views.view_panel_technical import registrar_tratamento_view





from .views import extrair_enderecos_view, gerar_etiquetas_view,dashboard_view,criar_user_view,ver_usuario_view,mover_rota_view, ordenar_rota_view




app_name = 'transportes'

urlpatterns = [
     path("registrar-tratamento/<int:uid>/", registrar_tratamento_view, name="registrar_tratamento"),
    path('painel/controle/',dashboard_view, name='controle'),
    path("gerar-etiquetas/", gerar_etiquetas_view, name="gerar_etiquetas"),
    path("extrair-enderecos/", extrair_enderecos_view, name="extrair_enderecos"),
    path("painel/Dashboard/", painel_Dashboard_view, name="Dashboard"),
    
    path("Ferramentas/config/", config_context_view, name="config_context"),
    path("Ferramentas/criar-usuarios/", criar_user_view, name="criar_usuario"),
    path("Ferramentas/ver-usuarios/", ver_usuario_view, name="ver_usuario"),
    path("Ferramentas/mover-rotas/", mover_rota_view, name="mover_rota"),
    path("Ferramentas/ordenar_rotas/", ordenar_rota_view, name="ordenar_rota"),
]
