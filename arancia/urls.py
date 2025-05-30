from django.urls import path
from .views import index, consulta_id_form, pre_recebimento, recebimento, registrar_romaneio,consulta_id_table,consulta_pre_recebimento

app_name = 'arancia'

urlpatterns = [
    path('', index, name='index'),
    path('consulta-id/', consulta_id_form, name='consulta_id_form'),
    path('consulta-id/<str:id>/', consulta_id_table, name='consulta_id_table'),
    path('pre-recebimento/', pre_recebimento, name='pre_recebimento'),
    path('recebimento/', recebimento, name='recebimento'),
    path('consulta/pre-recebimento/', consulta_pre_recebimento, name='consulta_pre_recebimento'),
]