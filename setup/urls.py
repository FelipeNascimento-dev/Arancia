from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from setup.local_settings import BASE_PATH


urlpatterns = [
    path(BASE_PATH, include('logistica.urls')),
    path(BASE_PATH, include('transportes.urls')),
    path(BASE_PATH, include('backoffice.urls')),
    path(BASE_PATH, include('mural.urls')),
    path(BASE_PATH, include('crm.urls')),

    path(f'{BASE_PATH}admin/', admin.site.urls),
]

# if settings.LOCAL_DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
