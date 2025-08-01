from .views import UserLoginView
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import index, consulta_id_form, pre_recebimento, \
recebimento, registrar_romaneio,consulta_id_table, consulta_result, \
btn_voltar, estorno_result, reserva_equip, saida_campo, estorno_reserva, \
cancelamento_saida_campo, consulta_ma84, btn_ma_voltar, consulta_ec01, btn_ec_voltar, \
logout_confirm_view, logout_view, registrar_usuario

app_name = 'logistica'

urlpatterns = [
    path('', index, name='index'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', registrar_usuario, name='register'),
    path('logout/', logout_confirm_view, name='logout_confirm'),
    path('logout/confirm/', logout_view, name='logout'),
    path('consulta-id/', consulta_id_form, name='consulta_id_form'),
    path('consulta-id/<str:id>/', consulta_id_table, name='consulta_id_table'),
    path('pre-recebimento/', pre_recebimento, name='pre_recebimento'),
    path('recebimento/', recebimento, name='recebimento'),
    path('consulta/resultados/<str:tp_reg>/', consulta_result, name='consulta_resultados'),
    path('consulta/resultados/<str:tp_reg>/voltar/', btn_voltar, name='btn_voltar'),
    path('estorno/', estorno_result, name='estorno'),
    path('reserva-equip/', reserva_equip, name='reserva_equip'),
    path('saida-campo/', saida_campo, name='saida_campo'),
    path('estorno/reserva-equip/', estorno_reserva, name='estorno_reserva'),
    path('cancelamento/saida-campo/', cancelamento_saida_campo, name='cancelamento_saida_campo'),
    path('consulta-ma/<str:tp_reg>/', consulta_ma84, name='consulta_result_ma'),
    path('consulta-ma/<str:tp_reg>/voltar/', btn_ma_voltar, name='btn_ma_voltar'),
    path('consulta-ec/<str:tp_reg>/', consulta_ec01, name='consulta_result_ec'),
    path('consulta-ec/<str:tp_reg>/voltar/', btn_ec_voltar, name='btn_ec_voltar'),
]