# API Recetas Django

Una API REST desarrollada con Django para gestión de recetas de cocina.

## Descripción

Este proyecto es una API REST construida con Django y Django REST Framework que permite gestionar recetas de cocina, incluyendo funcionalidades como:

- Gestión de usuarios
- CRUD de recetas
- Categorización de recetas
- Búsqueda y filtrado

## Tecnologías utilizadas

- Python 3.x
- Django
- Django REST Framework
- SQLite (desarrollo)

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/api_recetas_django.git
cd api_recetas_django
```

2. Crea un entorno virtual:
```bash
python -m venv venv
```

3. Activa el entorno virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

5. Crea un archivo `.env` basado en `.env.example` y configura tus variables de entorno.

6. Ejecuta las migraciones:
```bash
python manage.py migrate
```

7. Crea un superusuario (opcional):
```bash
python manage.py createsuperuser
```

8. Ejecuta el servidor de desarrollo:
```bash
python manage.py runserver
```

## Estructura del proyecto

```
api_recetas_django/
├── apps/
│   └── usuarios/
├── quanticook/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## API Endpoints

Documentación de los endpoints disponibles:

- `/api/usuarios/` - Gestión de usuarios
- (Agregar más endpoints según se desarrollen)

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

- Autor: [Tu Nombre]
- Email: [tu-email@ejemplo.com]
- GitHub: [tu-usuario]
