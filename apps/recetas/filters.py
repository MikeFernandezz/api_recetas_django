import django_filters
from django.db.models import Q
from .models import Receta


class RecetaFilter(django_filters.FilterSet):
    """
    Filtros avanzados para recetas
    """
    
    # Filtros por tiempo
    tiempo_max = django_filters.NumberFilter(
        field_name='tiempo_preparacion', 
        lookup_expr='lte',
        help_text="Tiempo máximo de preparación en minutos"
    )
    
    tiempo_total_max = django_filters.NumberFilter(
        method='filter_tiempo_total',
        help_text="Tiempo total máximo (preparación + cocción) en minutos"
    )
    
    # Filtros por dificultad
    dificultad = django_filters.MultipleChoiceFilter(
        choices=Receta._meta.get_field('dificultad').choices,
        help_text="Filtrar por nivel de dificultad"
    )
    
    # Filtros por porciones
    porciones_min = django_filters.NumberFilter(
        field_name='porciones',
        lookup_expr='gte',
        help_text="Número mínimo de porciones"
    )
    
    porciones_max = django_filters.NumberFilter(
        field_name='porciones',
        lookup_expr='lte',
        help_text="Número máximo de porciones"
    )
    
    # Filtro por ingredientes
    ingredientes = django_filters.CharFilter(
        method='filter_por_ingredientes',
        help_text="Buscar por ingredientes (separados por coma)"
    )
    
    # Filtro por categoría
    categoria = django_filters.CharFilter(
        field_name='categoria__slug',
        lookup_expr='iexact',
        help_text="Filtrar por categoría usando slug"
    )
    
    # Filtro por autor
    autor = django_filters.CharFilter(
        field_name='autor__username',
        lookup_expr='icontains',
        help_text="Filtrar por nombre de usuario del autor"
    )
    
    # Filtros por estado
    destacada = django_filters.BooleanFilter(
        field_name='destacada',
        help_text="Mostrar solo recetas destacadas"
    )
    
    # Filtro por calorías
    calorias_max = django_filters.NumberFilter(
        field_name='calorias_por_porcion',
        lookup_expr='lte',
        help_text="Máximo de calorías por porción"
    )
    
    # Filtro por fecha
    fecha_desde = django_filters.DateFilter(
        field_name='fecha_creacion',
        lookup_expr='gte',
        help_text="Recetas creadas desde esta fecha"
    )
    
    fecha_hasta = django_filters.DateFilter(
        field_name='fecha_creacion',
        lookup_expr='lte',
        help_text="Recetas creadas hasta esta fecha"
    )
    
    class Meta:
        model = Receta
        fields = {
            'titulo': ['icontains'],
            'descripcion': ['icontains'],
        }
    
    def filter_tiempo_total(self, queryset, name, value):
        """Filtrar por tiempo total (preparación + cocción)"""
        if value:
            return queryset.extra(
                where=["tiempo_preparacion + tiempo_coccion <= %s"],
                params=[value]
            )
        return queryset
    
    def filter_por_ingredientes(self, queryset, name, value):
        """Filtrar recetas que contengan los ingredientes especificados"""
        if value:
            ingredientes = [ing.strip() for ing in value.split(',')]
            for ingrediente in ingredientes:
                if ingrediente:
                    queryset = queryset.filter(
                        ingredientes_detalle__ingrediente__nombre__icontains=ingrediente
                    )
            return queryset.distinct()
        return queryset
