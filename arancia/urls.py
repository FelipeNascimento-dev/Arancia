from django.urls import path
from . import views

app_name = 'arancia'

urlpatterns = [
    path('', views.index, name='index'),
    path('romaneio/', views.romaneio, name='romaneio'),
    path('revisar/', views.revisar, name='revisar'),
    path('rastreio/', views.rastreio, name='rastreio'),
    path('despacho/', views.despacho, name='despacho'),
    path('entrega/paec/', views.entrega_paec, name='entrega_paec'),
    path('entrega/picpac/', views.entrega_picpac, name='entrega_picpac'),
    path('estorno/paec/', views.estorno_paec, name='estorno_paec'),
    path('estorno/picpac/', views.estorno_picpac, name='estorno_picpac'),
    path('estorno/rom/', views.estorno_rom, name='estorno_rom'),
    path('consulta/', views.consulta_id, name='consulta_id'),
    path('pre-recebimento/', views.pre_recebimento, name='pre_recebimento'),
]