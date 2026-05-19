from django.urls import path
from .views import *

app_name = 'mural'

urlpatterns = [
    path('', mural, name='mural'),
    path("mural/gerenciamento/", gerenciar_mural, name="mural_gerenciamento"),
]
