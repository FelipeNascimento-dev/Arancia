from .views import UserLoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path
from .viewsV2 import trackingIPV2
from .views import *

app_name = 'logistica'

urls_User = [
    path('', index, name='index'),
    path('toggle-db/', toggle_db, name='toggle_db'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', registrar_usuario, name='register'),
    path('logout/', logout_confirm_view, name='logout_confirm'),
    path('logout/confirm/', logout_view, name='logout'),
    path("settings/", settings_view, name="settings"),
    path("settings/password/", UserPasswordChangeView.as_view(),
         name="password_change"),
]

urls_LastmileB2C = [
    path('consulta-id/', consulta_id_form, name='consulta_id_form'),
    path('consulta-id/<str:id>/', consulta_id_table, name='consulta_id_table'),
    path('pre-recebimento/<str:tp_reg>/',
         pre_recebimento, name='pre_recebimento'),
    path('recebimento/<str:tp_reg>/', recebimento, name='recebimento'),
    path('estorno/<str:tp_reg>/', pre_recebimento,
         name='estorno_pre_recebimento'),
    path('estorno/<str:tp_reg>/', recebimento, name='estorno_recebimento'),
    path('consulta/resultados/', consulta_result, name='consulta_resultados'),
    path('consulta/resultados/voltar/', btn_voltar, name='btn_voltar'),
    path('reserva-equip/<str:tp_reg>/', reserva_equip, name='reserva_equip'),
    path('estorno/reserva-equip/<str:tp_reg>/',
         reserva_equip, name='estorno_reserva'),
    path('saida-campo/<str:tp_reg>/', saida_campo, name='saida_campo'),
    path('cancelamento/saida-campo/<str:tp_reg>/',
         saida_campo, name='cancelamento_saida_campo'),
    path('consulta-ma/', consulta_ma84, name='consulta_result_ma'),
    path('consulta-ma/voltar/', btn_ma_voltar, name='btn_ma_voltar'),
    path('consulta-ec/', consulta_ec01, name='consulta_result_ec'),
    path('consulta-ec/voltar/', btn_ec_voltar, name='btn_ec_voltar'),
    path('ip-spl/<str:code>/', trackingIPV2, name='pcp_simpl'),
    path('ip-spl/<str:code>/', trackingIPV2, name='retorno_picking_simpl'),
    path('ip-spl/<str:code>/', trackingIPV2, name='consolidacao_simpl'),
    path('ip-spl/<str:code>/', trackingIPV2, name='expedicao_simpl'),
    path('ip-spl/<str:code>/', trackingIPV2, name='troca_custodia_simpl'),

    path('ip/<str:code>/', trackingIP, name='pcp'),
    path('ip/<str:code>/', trackingIP, name='retorno_picking'),
    path('ip/<str:code>/', trackingIP, name='consolidacao'),
    path('ip/<str:code>/', trackingIP, name='expedicao'),
    path('ip/<str:code>/', trackingIP, name='troca_custodia'),

    path('extracao-pedidos/', extracao_pedidos, name='extracao_pedidos'),
    path('consulta-etiquetas/', consulta_etiquetas, name='consulta_etiquetas'),
    path('consulta-pedidos/', consulta_pedidos, name='consulta_pedidos'),
    path('recebimento-remessa/', recebimento_remessa, name='recebimento_remessa'),
    path('consultar-pedido/', order_consult, name='consultar_pedido'),
    path('buttons-order/<str:order>', button_desn, name='button_desn'),
    path('consultar-pedido/<str:order>/', order_detail, name='detalhe_pedido'),
    path('conferir-retirada', order_return_check, name='order_return_check'),
    path('reverse/consulta/', consult_rom, name='consultar_romaneio'),
    path('reverse/', reverse_create, name='reverse_create'),
    path('reverse/delete/<str:serial>/', delete_btn, name='delete_btn'),
    path('reverse/cancel/<str:id>/', cancel_btn, name='cancel_btn'),
    path('reverse/envio', send_quotes, name='send_quotes'),
    path('insucesso/insert/<str:order>/',
         unsuccessful_insert, name='unsuccessful_insert'),
]

urls_Gerenciamento = [
    path('user-ger/', user_ger, name='user_ger'),
    path('skill-ger/', skill_ger, name='skill_ger'),
]

urls_Checkin = [
    path('check/<str:vetor>/selecao-clientes/',
         client_select, name='client_select'),
    path('check-in/cliente/consult/', client_consult, name='client_consult'),
    path('check-in/order/select/', order_select, name='order_select'),
    path('check-in/registro/', client_checkin, name='client_checkin'),
    path('check-in/product/create/', product_create, name='product_create'),
]

urlpatterns = urls_User + urls_LastmileB2C + urls_Gerenciamento + urls_Checkin + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
