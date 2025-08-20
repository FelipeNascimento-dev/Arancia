from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('arancia/', include('logistica.urls')),
    path('arancia/admin/', admin.site.urls),
]
