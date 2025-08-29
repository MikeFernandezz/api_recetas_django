from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilExtendido


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del admin para el modelo Usuario personalizado
    """
    
    # Campos que se muestran en la lista
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'nivel_experiencia',
        'perfil_publico',
        'is_active',
        'fecha_creacion'
    )
    
    # Filtros laterales
    list_filter = (
        'nivel_experiencia',
        'perfil_publico', 
        'is_active',
        'is_staff',
        'fecha_creacion'
    )
    
    # Campos de búsqueda
    search_fields = ('username', 'email', 'first_name', 'last_name', 'pais')
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal Adicional', {
            'fields': (
                'biografia', 
                'avatar', 
                'fecha_nacimiento', 
                'pais'
            )
        }),
        ('Preferencias', {
            'fields': (
                'nivel_experiencia',
                'perfil_publico'
            )
        }),
    )
    
    # Campos para el formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': (
                'email',
                'first_name', 
                'last_name',
                'biografia',
                'nivel_experiencia'
            )
        }),
    )


@admin.register(PerfilExtendido)
class PerfilExtendidoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para PerfilExtendido
    """
    
    list_display = (
        'usuario',
        'total_recetas',
        'total_seguidores',
        'cuenta_verificada'
    )
    
    list_filter = ('cuenta_verificada',)
    search_fields = ('usuario__username', 'usuario__email')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Estadísticas', {
            'fields': (
                'total_recetas',
                'total_seguidores', 
                'total_siguiendo'
            )
        }),
        ('Redes Sociales', {
            'fields': ('instagram', 'youtube', 'blog_personal'),
            'classes': ('collapse',)  # Sección colapsable
        }),
        ('Verificación', {
            'fields': ('cuenta_verificada',)
        }),
    )
