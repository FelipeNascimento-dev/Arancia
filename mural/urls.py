from django.urls import path
from .views import gerenciar_mural, mural
from .views.view_mural import mural_items_feed

app_name = 'mural'

urlpatterns = [
    path('', mural, name='mural'),
    path("mural/items/", mural_items_feed, name="mural_items_feed"),
    path("mural/gerenciamento/", gerenciar_mural, name="mural_gerenciamento"),
]
