from .views import UserLoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path
from .viewsV2 import trackingIPV2
from .views import index, consulta_id_form, pre_recebimento, \
    recebimento, registrar_romaneio, consulta_id_table, consulta_result, \
    consulta_pedidos, recebimento_remessa, order_consult, button_desn, \
    btn_voltar, reserva_equip, saida_campo, order_detail, order_return_check, \
    consulta_ma84, btn_ma_voltar, consulta_ec01, btn_ec_voltar, consult_rom, \
    logout_confirm_view, logout_view, registrar_usuario, trackingIP, user_ger, skill_ger, \
    extracao_pedidos, consulta_etiquetas, settings_view, reverse_create, delete_btn, \
    cancel_btn, send_quotes, toggle_db, unsuccessful, unsuccessful_insert, \
    UserPasswordChangeView

app_name = 'logistica'

urlpatterns = [
    path('', index, name='index'),
    path('toggle-db/', toggle_db, name='toggle_db'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', registrar_usuario, name='register'),
    path('logout/', logout_confirm_view, name='logout_confirm'),
    path('logout/confirm/', logout_view, name='logout'),
    path("settings/", settings_view, name="settings"),
    path("settings/password/", UserPasswordChangeView.as_view(),
         name="password_change"),
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
    path('user-ger/', user_ger, name='user_ger'),
    path('skill-ger/', skill_ger, name='skill_ger'),
    path('reverse/consulta/', consult_rom, name='consultar_romaneio'),
    path('reverse/', reverse_create, name='reverse_create'),
    path('reverse/delete/<str:serial>/', delete_btn, name='delete_btn'),
    path('reverse/cancel/<str:id>/', cancel_btn, name='cancel_btn'),
    path('reverse/envio', send_quotes, name='send_quotes'),
    path('insucesso/', unsuccessful, name='unsuccessful'),
    path('insucesso/insert/<str:order>/',
         unsuccessful_insert, name='unsuccessful_insert'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
