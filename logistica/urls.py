from .views import UserLoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path
from .viewsV2 import trackingIPV2
from .views import index, consulta_id_form, pre_recebimento, \
    recebimento, registrar_romaneio, consulta_id_table, consulta_result, \
    consulta_pedidos, recebimento_remessa, entrada_pedido, \
    btn_voltar, reserva_equip, saida_campo, visu_pedido, fallback_check, \
    consulta_ma84, btn_ma_voltar, consulta_ec01, btn_ec_voltar, \
    logout_confirm_view, logout_view, registrar_usuario, trackingIP, \
    extracao_pedidos, consulta_etiquetas, settings_view, UserPasswordChangeView

app_name = 'logistica'

urlpatterns = [
    path('', index, name='index'),
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
    path('entrada-pedido/', entrada_pedido, name='entrada_pedido'),
    path('entrada-pedido/<str:order>/',
         visu_pedido, name='visu_pedido'),
    path('conferir-retirada', fallback_check, name='fallback_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
