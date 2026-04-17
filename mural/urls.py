from django.urls import path
from .views import *

app_name = 'mural'

urlpatterns = [
    path('home/', mural, name='mural'),
]
