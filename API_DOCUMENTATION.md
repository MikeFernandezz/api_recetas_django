# Documentación de la API de Quanticook

## **Estado Actual del Proyecto**

### **Completado:**
- ✅ Modelos de base de datos (Usuario, Receta, Categoría, Ingrediente, Rating, Favorito)
- ✅ Serializers completos para la API
- ✅ Admin personalizado y funcional
- ✅ Configuración inicial de Django REST Framework

### **En Proceso:**
- 🔄 ViewSets y URLs de la API
- 🔄 Sistema de autenticación
- 🔄 Filtros y búsquedas avanzadas

---

## **Endpoints de la API**

### **Base URL:** `http://127.0.0.1:8000/api/v1/`

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/recetas/` | GET, POST | Listar y crear recetas | 🔓 GET, 🔐 POST |
| `/recetas/{id}/` | GET, PUT, DELETE | Detalle, actualizar, eliminar receta | 🔓 GET, 🔐 PUT/DELETE (autor) |
| `/recetas/destacadas/` | GET | Recetas destacadas | 🔓 |
| `/recetas/mas_vistas/` | GET | Recetas más vistas | 🔓 |
| `/recetas/mejor_valoradas/` | GET | Recetas mejor valoradas | 🔓 |
| `/recetas/mis_recetas/` | GET | Mis recetas (usuario autenticado) | 🔐 |
| `/recetas/buscar_por_ingredientes/` | GET | Buscar por ingredientes | 🔓 |
| `/categorias/` | GET, POST | Gestión de categorías | 🔓 GET, 🔐 POST (admin) |
| `/ingredientes/` | GET, POST | Gestión de ingredientes | 🔓 GET, 🔐 POST |
| `/favoritos/` | GET, POST | Gestión de favoritos | 🔐 |
| `/ratings/` | GET, POST | Valoraciones de recetas | 🔐 |

---

## **Próximos Pasos - TO DO LIST**

### **CRÍTICO - Hacer AHORA:**

#### 1. **Completar ViewSets y URLs**
```bash
# Crear el archivo views.py para recetas
touch apps/recetas/views.py

# Crear URLs de la API
touch apps/recetas/api_urls.py
touch apps/usuarios/api_urls.py
touch apps/core/api_urls.py
```

#### 2. **Implementar ViewSets faltantes**
- [ ] `RecetaViewSet` - CRUD completo con acciones personalizadas
- [ ] `CategoriaViewSet` - Gestión de categorías
- [ ] `IngredienteViewSet` - Gestión de ingredientes
- [ ] `FavoritoViewSet` - Sistema de favoritos
- [ ] `RatingViewSet` - Sistema de valoraciones

#### 3. **Configurar URLs principales**
```python
# En quanticook/urls.py - Agregar URLs de API
path('api/v1/recetas/', include('apps.recetas.api_urls')),
```

### **IMPORTANTE - Esta semana:**

#### 4. **Sistema de Autenticación**
- [ ] Configurar Token Authentication
- [ ] Crear endpoints de registro/login
- [ ] Implementar permisos personalizados
- [ ] Validaciones de seguridad

#### 5. **Filtros y Búsquedas Avanzadas**
```python
# Implementar en ViewSets:
# - Filtro por categoría: ?categoria=italiana
# - Filtro por tiempo: ?tiempo_max=30
# - Filtro por dificultad: ?dificultad=facil
# - Búsqueda por título: ?search=pasta
# - Filtro por ingredientes: ?ingredientes=tomate,albahaca
```

#### 6. **Validaciones de Negocio**
- [ ] Un usuario solo puede valorar una receta una vez
- [ ] Solo el autor puede editar sus recetas
- [ ] Validaciones de campos (tiempo > 0, rating 1-5)
- [ ] Límites de uploads de imágenes

### **MEJORAS - Próximamente:**

#### 7. **Funcionalidades Avanzadas**
- [ ] Sistema de seguimiento de usuarios
- [ ] Comentarios en recetas
- [ ] Historial de recetas vistas
- [ ] Recomendaciones personalizadas
- [ ] Sistema de etiquetas/tags

#### 8. **Optimizaciones**
- [ ] Paginación personalizada
- [ ] Cache de consultas frecuentes
- [ ] Compresión de imágenes automática
- [ ] Búsqueda con Elasticsearch

#### 9. **Testing y Documentación**
- [ ] Tests unitarios para cada endpoint
- [ ] Tests de integración
- [ ] Documentación automática con Swagger
- [ ] Postman Collection

### 🔵 **FRONTEND - Futuro:**

#### 10. **Interfaz Web**
- [ ] Templates HTML básicos
- [ ] Formularios de recetas
- [ ] Galería de recetas
- [ ] Perfil de usuario
- [ ] Dashboard de estadísticas

#### 11. **API para Frontend**
- [ ] React/Vue.js integration
- [ ] Websockets para notificaciones
- [ ] PWA (Progressive Web App)

---

## 🚀 **Comandos para Continuar AHORA**

### Paso 1: Crear ViewSets básicos
```python
# apps/recetas/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Receta, Categoria, Ingrediente, Favorito, Rating
from .serializers import *

class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.filter(publicada=True)
    serializer_class = RecetaListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria', 'dificultad', 'autor']
    search_fields = ['titulo', 'descripcion']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecetaDetailSerializer
        elif self.action in ['create', 'update']:
            return RecetaCreateUpdateSerializer
        return RecetaListSerializer
```

### Paso 2: Crear URLs básicas
```python
# apps/recetas/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecetaViewSet

router = DefaultRouter()
router.register(r'recetas', RecetaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### Paso 3: Probar la API
```bash
python manage.py runserver
# Visitar: http://127.0.0.1:8000/api/v1/recetas/
```

---

## 🔧 **Estructura de Datos**

### **Modelo Receta**
```json
{
  "id": "uuid",
  "titulo": "string",
  "descripcion": "string", 
  "autor": {
    "id": "int",
    "username": "string",
    "nombre_completo": "string"
  },
  "categoria": {
    "id": "int",
    "nombre": "string",
    "slug": "string"
  },
  "tiempo_preparacion": "int",
  "tiempo_coccion": "int",
  "tiempo_total": "int",
  "dificultad": "string",
  "porciones": "int",
  "instrucciones": "string",
  "imagen_principal": "url",
  "ingredientes_detalle": [
    {
      "ingrediente": {
        "id": "int",
        "nombre": "string"
      },
      "cantidad": "string",
      "opcional": "boolean"
    }
  ],
  "rating_promedio": "float",
  "total_favoritos": "int",
  "vistas": "int",
  "es_favorito": "boolean"
}
```

### **Modelo Usuario**
```json
{
  "id": "int",
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "nombre_completo": "string",
  "avatar": "url",
  "nivel_experiencia": "string",
  "pais": "string",
  "fecha_creacion": "datetime"
}
```

---

## 🎯 **Ejemplos de Uso**

### **Listar recetas**
```http
GET /api/v1/recetas/
```

### **Buscar recetas por ingredientes**
```http
GET /api/v1/recetas/buscar_por_ingredientes/?ingredientes=tomate,cebolla
```

### **Filtrar recetas**
```http
GET /api/v1/recetas/?categoria=italiana&dificultad=facil&tiempo_max=30
```

### **Crear una receta**
```http
POST /api/v1/recetas/
Content-Type: application/json
Authorization: Token abc123

{
  "titulo": "Pasta Carbonara",
  "descripcion": "Deliciosa pasta italiana",
  "categoria": 1,
  "tiempo_preparacion": 15,
  "tiempo_coccion": 10,
  "dificultad": "intermedio",
  "porciones": 4,
  "instrucciones": "1. Hervir la pasta...",
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "cantidad": "400g",
      "opcional": false
    }
  ]
}
```

### **Valorar una receta**
```http
POST /api/v1/recetas/{id}/valorar/
Content-Type: application/json
Authorization: Token abc123

{
  "puntuacion": 5,
  "comentario": "¡Excelente receta!"
}
```

---

## 🎯 **Objetivos de la Próxima Sesión**

1. **Completar ViewSets básicos** (30 min)
2. **Configurar URLs de API** (15 min)
3. **Probar endpoints básicos** (15 min)
4. **Implementar autenticación** (30 min)
5. **Agregar filtros avanzados** (30 min)

## 📞 **¿Por dónde empezamos?**

¿Quieres que continuemos con:
1. **Crear los ViewSets** para que la API funcione
2. **Configurar autenticación** para proteger endpoints
3. **Implementar filtros** para búsquedas avanzadas
4. **Probar la API** con datos reales

**Recomendación:** Empezar con **ViewSets** para tener una API funcional básica.

---

## 📝 **Notas de Desarrollo**

- **Base de datos:** MySQL configurada
- **Framework:** Django 5.2 + Django REST Framework
- **Autenticación:** Token-based (pendiente configurar)
- **Entorno:** Virtual environment activado
- **Admin:** Funcional en `/admin/`

## 🔗 **Links Útiles**

- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Root:** http://127.0.0.1:8000/api/v1/
- **Documentación DRF:** https://www.django-rest-framework.org/
- **Django Filters:** https://django-filter.readthedocs.io/
