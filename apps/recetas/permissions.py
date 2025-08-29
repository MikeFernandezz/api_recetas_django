from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los propietarios de un objeto editarlo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request,
        # por lo que siempre permitiremos GET, HEAD o OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el propietario del objeto.
        return obj.autor == request.user


class IsOwner(permissions.BasePermission):
    """
    Permiso que solo permite acceso al propietario del objeto.
    """
    
    def has_object_permission(self, request, view, obj):
        # Solo el propietario puede acceder al objeto
        return obj.usuario == request.user


class IsRecipeOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso específico para recetas que permite lectura a todos
    pero escritura solo al autor de la receta.
    """
    
    def has_permission(self, request, view):
        # Permitir acceso de lectura a usuarios anónimos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Requerir autenticación para operaciones de escritura
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el autor de la receta
        return obj.autor == request.user


class CanRate(permissions.BasePermission):
    """
    Permiso para valorar recetas.
    Un usuario no puede valorar sus propias recetas.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Si es una receta, verificar que no sea del mismo usuario
        if hasattr(obj, 'autor'):
            return obj.autor != request.user
        
        # Si es un rating, verificar que sea del usuario autenticado
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return True
