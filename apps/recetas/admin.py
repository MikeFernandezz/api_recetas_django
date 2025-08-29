from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Categoria, Ingrediente, Receta, RecetaIngrediente, 
    Rating, Favorito, ImagenReceta
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Admin para categorías de cocina
    """
    list_display = ('nombre', 'activa', 'total_recetas', 'imagen_preview')
    list_filter = ('activa',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activa',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    def total_recetas(self, obj):
        """Muestra el total de recetas por categoría"""
        return obj.recetas.count()
    total_recetas.short_description = 'Total Recetas'
    
    def imagen_preview(self, obj):
        """Muestra una miniatura de la imagen"""
        if obj.imagen:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Vista Previa'


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    """
    Admin para ingredientes
    """
    list_display = ('nombre', 'categoria_ingrediente', 'total_usos')
    list_filter = ('categoria_ingrediente',)
    search_fields = ('nombre',)
    ordering = ('nombre',)
    
    def total_usos(self, obj):
        """Muestra en cuántas recetas se usa el ingrediente"""
        return obj.recetas_uso.count()
    total_usos.short_description = 'Usado en'


class RecetaIngredienteInline(admin.TabularInline):
    """
    Inline para gestionar ingredientes dentro de la receta
    """
    model = RecetaIngrediente
    extra = 3
    fields = ('ingrediente', 'cantidad', 'opcional')
    autocomplete_fields = ('ingrediente',)


class ImagenRecetaInline(admin.TabularInline):
    """
    Inline para gestionar imágenes adicionales de la receta
    """
    model = ImagenReceta
    extra = 2
    fields = ('imagen', 'descripcion', 'orden')
    readonly_fields = ('imagen_preview',)
    
    def imagen_preview(self, obj):
        """Muestra miniatura de la imagen"""
        if obj.imagen:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 5px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Vista Previa'


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    """
    Admin principal para recetas
    """
    list_display = (
        'titulo', 
        'autor', 
        'categoria', 
        'dificultad',
        'tiempo_total_display',
        'porciones',
        'publicada',
        'destacada',
        'rating_display',
        'vistas',
        'fecha_creacion'
    )
    
    list_filter = (
        'publicada',
        'destacada', 
        'dificultad',
        'categoria',
        'fecha_creacion',
        'autor'
    )
    
    search_fields = (
        'titulo', 
        'descripcion', 
        'autor__username',
        'autor__first_name',
        'autor__last_name'
    )
    
    list_editable = ('publicada', 'destacada')
    
    readonly_fields = (
        'id', 
        'fecha_creacion', 
        'fecha_actualizacion',
        'vistas',
        'rating_display',
        'total_favoritos_display',
        'imagen_preview'
    )
    
    autocomplete_fields = ('autor', 'categoria')
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'id',
                'titulo',
                'descripcion',
                'autor',
                'categoria'
            )
        }),
        ('Contenido', {
            'fields': (
                'instrucciones',
                'imagen_principal',
                'imagen_preview'
            )
        }),
        ('Detalles de Preparación', {
            'fields': (
                'tiempo_preparacion',
                'tiempo_coccion', 
                'dificultad',
                'porciones',
                'calorias_por_porcion'
            )
        }),
        ('Estado y Publicación', {
            'fields': (
                'publicada',
                'destacada'
            )
        }),
        ('Estadísticas', {
            'fields': (
                'vistas',
                'rating_display',
                'total_favoritos_display',
                'fecha_creacion',
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [RecetaIngredienteInline, ImagenRecetaInline]
    
    actions = ['marcar_como_publicada', 'marcar_como_borrador', 'marcar_como_destacada']
    
    def tiempo_total_display(self, obj):
        """Muestra el tiempo total de forma amigable"""
        total = obj.tiempo_total
        if total < 60:
            return f"{total} min"
        else:
            horas = total // 60
            minutos = total % 60
            if minutos:
                return f"{horas}h {minutos}min"
            return f"{horas}h"
    tiempo_total_display.short_description = 'Tiempo Total'
    
    def rating_display(self, obj):
        """Muestra el rating promedio con estrellas"""
        rating = obj.rating_promedio
        if rating:
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            return f"{stars} ({rating:.1f})"
        return "Sin calificar"
    rating_display.short_description = 'Rating'
    
    def total_favoritos_display(self, obj):
        """Muestra el total de favoritos"""
        total = obj.total_favoritos
        return f"♥ {total}"
    total_favoritos_display.short_description = 'Favoritos'
    
    def imagen_preview(self, obj):
        """Muestra vista previa de la imagen principal"""
        if obj.imagen_principal:
            return format_html(
                '<img src="{}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" />',
                obj.imagen_principal.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Vista Previa'
    
    # Acciones personalizadas
    def marcar_como_publicada(self, request, queryset):
        """Marca las recetas seleccionadas como publicadas"""
        updated = queryset.update(publicada=True)
        self.message_user(request, f'{updated} recetas marcadas como publicadas.')
    marcar_como_publicada.short_description = "Marcar como publicada"
    
    def marcar_como_borrador(self, request, queryset):
        """Marca las recetas seleccionadas como borrador"""
        updated = queryset.update(publicada=False)
        self.message_user(request, f'{updated} recetas marcadas como borrador.')
    marcar_como_borrador.short_description = "Marcar como borrador"
    
    def marcar_como_destacada(self, request, queryset):
        """Marca las recetas como destacadas"""
        updated = queryset.update(destacada=True)
        self.message_user(request, f'{updated} recetas marcadas como destacadas.')
    marcar_como_destacada.short_description = "Marcar como destacada"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """
    Admin para valoraciones
    """
    list_display = (
        'usuario',
        'receta_link',
        'puntuacion_display',
        'tiene_comentario',
        'fecha_creacion'
    )
    
    list_filter = (
        'puntuacion',
        'fecha_creacion'
    )
    
    search_fields = (
        'usuario__username',
        'receta__titulo',
        'comentario'
    )
    
    readonly_fields = ('fecha_creacion',)
    
    autocomplete_fields = ('usuario', 'receta')
    
    def receta_link(self, obj):
        """Link a la receta en el admin"""
        url = reverse('admin:recetas_receta_change', args=[obj.receta.pk])
        return format_html('<a href="{}">{}</a>', url, obj.receta.titulo)
    receta_link.short_description = 'Receta'
    
    def puntuacion_display(self, obj):
        """Muestra la puntuación con estrellas"""
        stars = "★" * obj.puntuacion + "☆" * (5 - obj.puntuacion)
        return f"{stars} ({obj.puntuacion})"
    puntuacion_display.short_description = 'Puntuación'
    
    def tiene_comentario(self, obj):
        """Indica si tiene comentario"""
        return "✓" if obj.comentario else "✗"
    tiene_comentario.short_description = 'Comentario'
    tiene_comentario.boolean = True


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    """
    Admin para favoritos
    """
    list_display = (
        'usuario',
        'receta_link',
        'fecha_agregado'
    )
    
    list_filter = ('fecha_agregado',)
    
    search_fields = (
        'usuario__username',
        'receta__titulo'
    )
    
    readonly_fields = ('fecha_agregado',)
    
    autocomplete_fields = ('usuario', 'receta')
    
    def receta_link(self, obj):
        """Link a la receta en el admin"""
        url = reverse('admin:recetas_receta_change', args=[obj.receta.pk])
        return format_html('<a href="{}">{}</a>', url, obj.receta.titulo)
    receta_link.short_description = 'Receta'


@admin.register(ImagenReceta)
class ImagenRecetaAdmin(admin.ModelAdmin):
    """
    Admin para imágenes adicionales de recetas
    """
    list_display = (
        'receta_link',
        'descripcion',
        'orden',
        'imagen_preview',
        'fecha_subida'
    )
    
    list_filter = ('fecha_subida',)
    
    search_fields = (
        'receta__titulo',
        'descripcion'
    )
    
    readonly_fields = ('fecha_subida', 'imagen_preview')
    
    autocomplete_fields = ('receta',)
    
    def receta_link(self, obj):
        """Link a la receta en el admin"""
        url = reverse('admin:recetas_receta_change', args=[obj.receta.pk])
        return format_html('<a href="{}">{}</a>', url, obj.receta.titulo)
    receta_link.short_description = 'Receta'
    
    def imagen_preview(self, obj):
        """Muestra vista previa de la imagen"""
        if obj.imagen:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 5px; object-fit: cover;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = 'Vista Previa'


# Configuración global del admin
admin.site.site_header = "Quanticook Admin"
admin.site.site_title = "Quanticook"
admin.site.index_title = "Panel de Administración de Quanticook"
