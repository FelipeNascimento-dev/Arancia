from django.urls import path

from backoffice.views import   importar_excel_view, baixar_duplicados_view






app_name = 'backoffice'

urlpatterns = [
    path('importar-excel/', importar_excel_view, name='importar_excel'),
    path("baixar-duplicados/", baixar_duplicados_view, name="baixar_duplicados"),
]