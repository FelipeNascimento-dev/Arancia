from django.urls import path
from . import views

app_name = 'arancia'

urlpatterns = [
    path('', views.index, name='index'),
    path('consulta/', views.consulta_id, name='consulta_id'),
    path('pre-recebimento/', views.pre_recebimento, name='pre_recebimento'),
    path('recebimento/', views.recebimento, name='recebimento'),
]