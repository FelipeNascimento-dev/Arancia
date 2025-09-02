
from django.urls import path
from .views import dashboard_view

app_name = 'transportes'

urlpatterns = [

    path('painel/',dashboard_view, name='painel'),

]

