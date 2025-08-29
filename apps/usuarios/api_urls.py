from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Por ahora vacío, aquí irán los ViewSets de usuarios
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
