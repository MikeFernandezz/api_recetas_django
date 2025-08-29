from django.http import JsonResponse
from django.shortcuts import render


def api_home(request):
    """
    Vista de bienvenida para la API de Quanticook
    """
    if request.content_type == 'application/json' or request.META.get('HTTP_ACCEPT') == 'application/json':
        # Respuesta JSON para clientes API
        return JsonResponse({
            'mensaje': 'Bienvenido a la API de Quanticook',
            'version': 'v1',
            'endpoints': {
                'recetas': '/api/v1/recetas/',
                'categorias': '/api/v1/categorias/',
                'ingredientes': '/api/v1/ingredientes/',
                'admin': '/admin/',
                'api_auth': '/api-auth/',
            },
            'documentacion': 'En desarrollo',
            'estado': 'Funcionando ✅'
        })
    else:
        # Respuesta HTML para navegadores
        context = {
            'titulo': 'Quanticook API',
            'version': 'v1.0.0',
            'endpoints': [
                {'nombre': 'Recetas', 'url': '/api/v1/recetas/', 'descripcion': 'CRUD completo de recetas'},
                {'nombre': 'Categorías', 'url': '/api/v1/categorias/', 'descripcion': 'Gestión de categorías de cocina'},
                {'nombre': 'Ingredientes', 'url': '/api/v1/ingredientes/', 'descripcion': 'Base de datos de ingredientes'},
                {'nombre': 'Admin', 'url': '/admin/', 'descripcion': 'Panel de administración'},
            ]
        }
        return render(request, 'home.html', context)
