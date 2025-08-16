from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('arancia/', include('logistica.urls')),
    path('admin/', admin.site.urls),
]
