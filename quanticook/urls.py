"""
URL configuration for quanticook project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # Página de inicio
    path('', include('apps.core.urls')),
    
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # API de Quanticook
    path('api/v1/', include('apps.recetas.api_urls')),
    path('api/v1/usuarios/', include('apps.usuarios.api_urls')),
    
    # Autenticación de la API
    path('api-auth/', include('rest_framework.urls')),
    
    # Documentación de la API (comentado temporalmente)
    # path('docs/', include_docs_urls(title='Quanticook API')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
