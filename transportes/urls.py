from django.urls import path

from transportes.views.View_session import config_context_view
from transportes.views.iframe import painel_Dashboard_view
from transportes.views.scripting_view import scripting_view
from transportes.views.view_panel_technical import registrar_tratamento_view
from .views import extrair_enderecos_view, gerar_etiquetas_view, dashboard_view, criar_user_view, ver_usuario_view, mover_rota_view, ordenar_rota_view
from .views import consulta_os_pend, lista_tecnicos, consulta_os, detalhe_os, consulta_os_transp, detalhe_os_transp, buscar_motoristas

app_name = 'transportes'

urlpatterns = [
    path("registrar-tratamento/<int:uid>/",
         registrar_tratamento_view, name="registrar_tratamento"),
    path('painel/controle/', dashboard_view, name='controle'),
    path("gerar-etiquetas/", gerar_etiquetas_view, name="gerar_etiquetas"),
    path("extrair-enderecos/", extrair_enderecos_view, name="extrair_enderecos"),
    path("painel/Dashboard/", painel_Dashboard_view, name="Dashboard"),

    path("Ferramentas/config/", config_context_view, name="config_context"),
    path("Ferramentas/criar-usuarios/", criar_user_view, name="criar_usuario"),
    path("Ferramentas/ver-usuarios/", ver_usuario_view, name="ver_usuario"),
    path("Ferramentas/mover-rotas/", mover_rota_view, name="mover_rota"),
    path("Ferramentas/ordenar-rotas/", ordenar_rota_view, name="ordenar_rota"),
    path("Ferramentas/roteirizacao/", scripting_view, name="scripting"),


    path("chamados/consulta-os/pendentes/",
         consulta_os_pend, name="consulta_os_pend"),
    path("chamados/consulta-os/", consulta_os, name="consulta_os"),
    path("chamados/detalhe-os/<path:os>/", detalhe_os, name="detalhe_os"),
    path("chamados/lista-tecnicos/", lista_tecnicos, name="lista_tecnicos"),

    path("detalhe-os/<path:order_number>/",
         detalhe_os_transp, name="detalhe_os_transp"),
    path("buscar-motoristas/", buscar_motoristas, name="buscar_motoristas"),
    path("consulta-os-transp/", consulta_os_transp, name="consulta_os_transp"),
]
