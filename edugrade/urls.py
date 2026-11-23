"""
URL configuration for edugrade project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import superuser_admin_site

urlpatterns = [
    path('admin/', superuser_admin_site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
