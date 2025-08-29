from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404

from .models import (
    Categoria, Ingrediente, Receta, Rating, Favorito
)
from .serializers import (
    CategoriaSerializer, IngredienteSerializer,
    RecetaListSerializer, RecetaDetailSerializer, RecetaCreateUpdateSerializer,
    RatingSerializer, FavoritoSerializer, EstadisticasRecetaSerializer
)
from .filters import RecetaFilter
from .permissions import IsOwnerOrReadOnly


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de cocina
    """
    queryset = Categoria.objects.filter(activa=True).annotate(
        total_recetas=Count('recetas', filter=Q(recetas__publicada=True))
    )
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'total_recetas']
    ordering = ['nombre']
    
    @action(detail=True, methods=['get'])
    def recetas(self, request, pk=None):
        """Obtiene las recetas de una categoría específica"""
        categoria = self.get_object()
        recetas = Receta.objects.filter(
            categoria=categoria, 
            publicada=True
        ).select_related('autor', 'categoria')
        
        serializer = RecetaListSerializer(recetas, many=True, context={'request': request})
        return Response(serializer.data)


class IngredienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar ingredientes
    """
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre']
    filterset_fields = ['categoria_ingrediente']
    ordering_fields = ['nombre']
    ordering = ['nombre']
    
    @action(detail=False, methods=['get'])
    def mas_usados(self, request):
        """Obtiene los ingredientes más utilizados"""
        ingredientes = Ingrediente.objects.annotate(
            total_uso=Count('recetas_uso')
        ).filter(total_uso__gt=0).order_by('-total_uso')[:20]
        
        serializer = self.get_serializer(ingredientes, many=True)
        return Response(serializer.data)


class RecetaViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para gestionar recetas
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecetaFilter
    search_fields = ['titulo', 'descripcion', 'instrucciones']
    ordering_fields = [
        'fecha_creacion', 'tiempo_preparacion', 'tiempo_coccion', 
        'dificultad', 'vistas', 'rating_promedio'
    ]
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """Queryset optimizado con select_related y prefetch_related"""
        queryset = Receta.objects.select_related(
            'autor', 'categoria'
        ).prefetch_related(
            'ingredientes_detalle__ingrediente',
            'imagenes_adicionales',
            'ratings',
            'favoritos'
        ).annotate(
            rating_promedio=Avg('ratings__puntuacion'),
            total_favoritos=Count('favoritos')
        )
        
        # Filtrar por estado de publicación según el usuario
        if self.request.user.is_authenticated:
            # Los usuarios autenticados ven sus propias recetas (publicadas y borradores)
            # y las recetas publicadas de otros
            queryset = queryset.filter(
                Q(publicada=True) | Q(autor=self.request.user)
            )
        else:
            # Los usuarios anónimos solo ven recetas publicadas
            queryset = queryset.filter(publicada=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return RecetaListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecetaCreateUpdateSerializer
        else:
            return RecetaDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementar vistas al obtener el detalle"""
        instance = self.get_object()
        instance.incrementar_vistas()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorito(self, request, pk=None):
        """Agregar o quitar de favoritos"""
        receta = self.get_object()
        favorito, created = Favorito.objects.get_or_create(
            usuario=request.user,
            receta=receta
        )
        
        if not created:
            favorito.delete()
            return Response({'favorito': False, 'mensaje': 'Eliminado de favoritos'})
        else:
            return Response({'favorito': True, 'mensaje': 'Agregado a favoritos'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def valorar(self, request, pk=None):
        """Valorar una receta"""
        receta = self.get_object()
        
        # Verificar que no sea su propia receta
        if receta.autor == request.user:
            return Response(
                {'error': 'No puedes valorar tu propia receta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear o actualizar rating
        rating, created = Rating.objects.update_or_create(
            usuario=request.user,
            receta=receta,
            defaults={
                'puntuacion': request.data.get('puntuacion'),
                'comentario': request.data.get('comentario', '')
            }
        )
        
        serializer = RatingSerializer(rating)
        mensaje = 'Valoración creada' if created else 'Valoración actualizada'
        
        return Response({
            'mensaje': mensaje,
            'rating': serializer.data,
            'rating_promedio': receta.rating_promedio
        })
    
    @action(detail=False, methods=['get'])
    def destacadas(self, request):
        """Obtiene las recetas destacadas"""
        recetas = self.get_queryset().filter(destacada=True)[:10]
        serializer = RecetaListSerializer(recetas, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mas_vistas(self, request):
        """Obtiene las recetas más vistas"""
        recetas = self.get_queryset().order_by('-vistas')[:10]
        serializer = RecetaListSerializer(recetas, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mejor_valoradas(self, request):
        """Obtiene las recetas mejor valoradas"""
        recetas = self.get_queryset().filter(
            ratings__isnull=False
        ).order_by('-rating_promedio')[:10]
        serializer = RecetaListSerializer(recetas, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_recetas(self, request):
        """Obtiene las recetas del usuario autenticado"""
        recetas = self.get_queryset().filter(autor=request.user)
        serializer = RecetaListSerializer(recetas, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def buscar_por_ingredientes(self, request):
        """Buscar recetas por ingredientes específicos"""
        ingredientes = request.query_params.get('ingredientes', '').split(',')
        if not ingredientes or ingredientes == ['']:
            return Response({'error': 'Debe especificar al menos un ingrediente'})
        
        # Filtrar recetas que contengan todos los ingredientes especificados
        recetas = self.get_queryset()
        for ingrediente_nombre in ingredientes:
            recetas = recetas.filter(
                ingredientes_detalle__ingrediente__nombre__icontains=ingrediente_nombre.strip()
            )
        
        recetas = recetas.distinct()
        serializer = RecetaListSerializer(recetas, many=True, context={'request': request})
        return Response(serializer.data)


class RatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar valoraciones
    """
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['puntuacion', 'receta']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """Solo mostrar ratings del usuario autenticado"""
        return Rating.objects.filter(usuario=self.request.user)


class FavoritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar favoritos
    """
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-fecha_agregado']
    
    def get_queryset(self):
        """Solo mostrar favoritos del usuario autenticado"""
        return Favorito.objects.filter(usuario=self.request.user).select_related(
            'receta__autor', 'receta__categoria'
        )


class EstadisticasViewSet(viewsets.ViewSet):
    """
    ViewSet para estadísticas generales
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def generales(self, request):
        """Estadísticas generales de la plataforma"""
        data = {
            'total_recetas': Receta.objects.filter(publicada=True).count(),
            'total_usuarios': request.user.__class__.objects.count(),
            'total_categorias': Categoria.objects.filter(activa=True).count(),
            'total_ingredientes': Ingrediente.objects.count(),
        }
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def mis_estadisticas(self, request):
        """Estadísticas del usuario autenticado"""
        usuario = request.user
        data = {
            'mis_recetas': usuario.recetas.count(),
            'recetas_publicadas': usuario.recetas.filter(publicada=True).count(),
            'recetas_borradores': usuario.recetas.filter(publicada=False).count(),
            'total_favoritos': Favorito.objects.filter(usuario=usuario).count(),
            'ratings_dados': Rating.objects.filter(usuario=usuario).count(),
        }
        return Response(data)
