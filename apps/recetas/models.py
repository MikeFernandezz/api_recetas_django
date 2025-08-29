from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from PIL import Image
import uuid

User = get_user_model()


class Categoria(models.Model):
    """
    Categorías de cocina (italiana, mexicana, vegana, etc.)
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    slug = models.SlugField(unique=True, help_text="URL amigable")
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    """
    Ingredientes base para las recetas
    """
    nombre = models.CharField(max_length=100, unique=True)
    categoria_ingrediente = models.CharField(
        max_length=50,
        choices=[
            ('proteina', 'Proteína'),
            ('verdura', 'Verdura'),
            ('fruta', 'Fruta'),
            ('cereal', 'Cereal'),
            ('lacteo', 'Lácteo'),
            ('condimento', 'Condimento'),
            ('otro', 'Otro'),
        ],
        default='otro'
    )
    
    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Receta(models.Model):
    """
    Modelo principal de recetas para Quanticook
    """
    # Identificación única
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Información básica
    titulo = models.CharField(
        max_length=200,
        help_text="Nombre de la receta"
    )
    
    descripcion = models.TextField(
        max_length=1000,
        help_text="Descripción breve de la receta"
    )
    
    # Relaciones
    autor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='recetas'
    )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recetas'
    )
    
    # Tiempos (en minutos)
    tiempo_preparacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Tiempo de preparación en minutos"
    )
    
    tiempo_coccion = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Tiempo de cocción en minutos"
    )
    
    # Dificultad y porciones
    dificultad = models.CharField(
        max_length=15,
        choices=[
            ('muy_facil', 'Muy Fácil'),
            ('facil', 'Fácil'),
            ('intermedio', 'Intermedio'),
            ('dificil', 'Difícil'),
            ('muy_dificil', 'Muy Difícil'),
        ],
        default='facil'
    )
    
    porciones = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        default=4,
        help_text="Número de porciones que rinde la receta"
    )
    
    # Contenido
    instrucciones = models.TextField(
        help_text="Pasos detallados para preparar la receta"
    )
    
    # Información nutricional (opcional)
    calorias_por_porcion = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Calorías aproximadas por porción"
    )
    
    # Imágenes
    imagen_principal = models.ImageField(
        upload_to='recetas/principales/',
        blank=True,
        null=True,
        help_text="Imagen principal de la receta"
    )
    
    # Estados
    publicada = models.BooleanField(
        default=False,
        help_text="¿La receta está publicada públicamente?"
    )
    
    destacada = models.BooleanField(
        default=False,
        help_text="¿Es una receta destacada?"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Estadísticas
    vistas = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['publicada', '-fecha_creacion']),
            models.Index(fields=['categoria', 'publicada']),
            models.Index(fields=['autor', '-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.autor.username}"
    
    @property
    def tiempo_total(self):
        """Tiempo total de preparación + cocción"""
        return self.tiempo_preparacion + self.tiempo_coccion
    
    @property
    def rating_promedio(self):
        """Promedio de ratings de la receta"""
        ratings = self.ratings.all()
        if ratings:
            return sum(r.puntuacion for r in ratings) / len(ratings)
        return 0
    
    @property
    def total_favoritos(self):
        """Total de usuarios que tienen esta receta como favorita"""
        return self.favoritos.count()
    
    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
    
    def save(self, *args, **kwargs):
        """Redimensionar imagen al guardar"""
        super().save(*args, **kwargs)
        
        if self.imagen_principal:
            img = Image.open(self.imagen_principal.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.imagen_principal.path)


class RecetaIngrediente(models.Model):
    """
    Relación muchos a muchos entre Receta e Ingrediente con cantidad
    """
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name='ingredientes_detalle'
    )
    
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='recetas_uso'
    )
    
    cantidad = models.CharField(
        max_length=100,
        help_text="Ej: 2 tazas, 500g, al gusto"
    )
    
    opcional = models.BooleanField(
        default=False,
        help_text="¿Es un ingrediente opcional?"
    )
    
    class Meta:
        unique_together = ['receta', 'ingrediente']
        verbose_name = "Ingrediente de Receta"
        verbose_name_plural = "Ingredientes de Recetas"
    
    def __str__(self):
        return f"{self.cantidad} de {self.ingrediente.nombre}"


class Rating(models.Model):
    """
    Valoraciones de las recetas por usuarios
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings_dados'
    )
    
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    
    puntuacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Puntuación de 1 a 5 estrellas"
    )
    
    comentario = models.TextField(
        max_length=500,
        blank=True,
        help_text="Comentario opcional sobre la receta"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'receta']
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.receta.titulo} ({self.puntuacion}★)"


class Favorito(models.Model):
    """
    Recetas favoritas de los usuarios
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'receta']
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"{self.usuario.username} ♥ {self.receta.titulo}"


class ImagenReceta(models.Model):
    """
    Imágenes adicionales para las recetas (galería)
    """
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name='imagenes_adicionales'
    )
    
    imagen = models.ImageField(
        upload_to='recetas/galeria/',
        help_text="Imagen adicional de la receta"
    )
    
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        help_text="Descripción de la imagen"
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de visualización"
    )
    
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Receta"
        verbose_name_plural = "Imágenes de Recetas"
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        return f"Imagen de {self.receta.titulo}"
