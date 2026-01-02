from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('arancia/', include('logistica.urls')),
    path('arancia/', include('transportes.urls')),
    path('arancia/', include('backoffice.urls')),

    path('arancia/admin/', admin.site.urls),
]

# if settings.LOCAL_DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
