from django.urls import path
from .views import index, consulta_id, pre_recebimento, recebimento, registrar_romaneio

app_name = 'arancia'

urlpatterns = [
    path('', index, name='index'),
    path('consulta/', consulta_id, name='consulta_id'),
    path('pre-recebimento/', pre_recebimento, name='pre_recebimento'),
    path('recebimento/', recebimento, name='recebimento'),
]