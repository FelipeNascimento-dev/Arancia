from django.urls import path

from transportes.views.View_session import config_context_view
from transportes.views.iframe import painel_Dashboard_view
from transportes.views.scripting_view import scripting_view
from transportes.views.view_panel_technical import registrar_tratamento_view
from .views import extrair_enderecos_view, gerar_etiquetas_view, criar_user_view, ver_usuario_view, mover_rota_view, ordenar_rota_view
from .views import consulta_os_pend, lista_tecnicos, consulta_os, detalhe_os, consulta_os_transp, detalhe_os_transp, buscar_motoristas, buscar_motoristas_travels, buscar_veiculos
from .views import lista_viagens, detalhe_viagem, criar_os_transp, buscar_locais, skill_customer, skill_transport, driver_ger, vehicle_ger, atribuir_motorista_viagens_manual, imprimir_os_viagens
from .views.views_transportes.view_lista_viagens_actions import (
    lista_viagens_atrelar_motorista,
    lista_viagens_criar_evento_lote,
    lista_viagens_export,
    lista_viagens_preparar_eventos,
)
from .views.views_transportes.api_listas_transportes import (
    api_consulta_os_list,
    api_lista_viagens_list,
    api_order_travels,
    api_travel_events,
)
from .views.dashboard_view import dashboard_view
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
    path("buscar-veiculos/", buscar_veiculos, name="buscar_veiculos"),
    path("consulta-os-transp/", consulta_os_transp, name="consulta_os_transp"),
    path("criar-os/", criar_os_transp, name="criar_os_transp"),
    path("buscar-locais/", buscar_locais, name="buscar_locais"),
    path("lista-viagens/", lista_viagens, name="lista_viagens"),
    path("lista-viagens/exportar/", lista_viagens_export, name="lista_viagens_export"),
    path(
        "lista-viagens/preparar-eventos/",
        lista_viagens_preparar_eventos,
        name="lista_viagens_preparar_eventos",
    ),
    path(
        "lista-viagens/atrelar-motorista/",
        lista_viagens_atrelar_motorista,
        name="lista_viagens_atrelar_motorista",
    ),
    path(
        "lista-viagens/criar-evento-lote/",
        lista_viagens_criar_evento_lote,
        name="lista_viagens_criar_evento_lote",
    ),
    path(
        "lista-viagens/api/travel-events/<int:travel_id>/",
        api_travel_events,
        name="api_travel_events",
    ),
    path(
        "consulta-os-transp/api/order-travels/",
        api_order_travels,
        name="api_order_travels",
    ),
    path(
        "consulta-os-transp/api/list/",
        api_consulta_os_list,
        name="api_consulta_os_list",
    ),
    path(
        "lista-viagens/api/list/",
        api_lista_viagens_list,
        name="api_lista_viagens_list",
    ),
    path("lista-viagens/imprimir-os/", imprimir_os_viagens, name="imprimir_os_viagens"),
    path("detalhe-viagem/<int:id_viagem>/",
         detalhe_viagem, name="detalhe_viagem"),
    path("gerenciamento/customer/", skill_customer, name="skill_customer"),
    path("gerenciamento/transport/", skill_transport, name="skill_transport"),
    path("gerenciamento/drivers/", driver_ger, name="driver_ger"),
    path("gerenciamento/veiculos/", vehicle_ger, name="vehicle_ger"),
    path("buscar-motoristas/travels", buscar_motoristas_travels,
         name="buscar_motoristas_travels"),
    path("atribuir-motoristas/", atribuir_motorista_viagens_manual,
         name="atribuir_motorista_viagens_manual"),
]
