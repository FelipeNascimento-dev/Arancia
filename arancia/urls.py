from django.urls import path
from .views import index, consulta_id_form, pre_recebimento, \
recebimento, registrar_romaneio,consulta_id_table, consulta_result, \
btn_voltar, estorno_result, reserva_equip, saida_campo

app_name = 'arancia'

urlpatterns = [
    path('', index, name='index'),
    path('consulta-id/', consulta_id_form, name='consulta_id_form'),
    path('consulta-id/<str:id>/', consulta_id_table, name='consulta_id_table'),
    path('pre-recebimento/', pre_recebimento, name='pre_recebimento'),
    path('recebimento/', recebimento, name='recebimento'),
    path('consulta/resultados/<str:tp_reg>/', consulta_result, name='consulta_resultados'),
    path('consulta/resultados/<str:tp_reg>/voltar/', btn_voltar, name='btn_voltar'),
    path('estorno/', estorno_result, name='estorno'),
    path('reserva-equip/', reserva_equip, name='reserva_equip'),
    path('saida-campo/', saida_campo, name='saida_campo'),
]