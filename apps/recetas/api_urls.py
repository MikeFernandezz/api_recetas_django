from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, IngredienteViewSet, RecetaViewSet,
    RatingViewSet, FavoritoViewSet, EstadisticasViewSet
)

# Crear el router principal
router = DefaultRouter()

# Registrar los ViewSets
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'ingredientes', IngredienteViewSet, basename='ingrediente')
router.register(r'recetas', RecetaViewSet, basename='receta')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'favoritos', FavoritoViewSet, basename='favorito')
router.register(r'estadisticas', EstadisticasViewSet, basename='estadisticas')

# URLs de la API
urlpatterns = [
    path('', include(router.urls)),
]
