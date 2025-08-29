from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para Quanticook
    Extiende el modelo User de Django con campos adicionales
    """
    
    # Campos adicionales para el perfil
    biografia = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="Cuéntanos un poco sobre ti y tu pasión por la cocina"
    )
    
    avatar = models.ImageField(
        upload_to='avatares/', 
        blank=True, 
        null=True,
        help_text="Foto de perfil"
    )
    
    fecha_nacimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Tu fecha de nacimiento"
    )
    
    pais = models.CharField(
        max_length=100, 
        blank=True,
        help_text="País de origen"
    )
    
    # Preferencias culinarias
    nivel_experiencia = models.CharField(
        max_length=20,
        choices=[
            ('principiante', 'Principiante'),
            ('intermedio', 'Intermedio'),
            ('avanzado', 'Avanzado'),
            ('chef', 'Chef Profesional'),
        ],
        default='principiante',
        help_text="Tu nivel de experiencia en la cocina"
    )
    
    # Configuración de privacidad
    perfil_publico = models.BooleanField(
        default=True,
        help_text="¿Quieres que otros usuarios vean tu perfil?"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
    def __str__(self):
        return f"{self.username} - {self.get_full_name() or self.email}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        """
        Método personalizado para redimensionar avatar al guardar
        """
        super().save(*args, **kwargs)
        
        # Redimensionar avatar si existe
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)


class PerfilExtendido(models.Model):
    """
    Información adicional del perfil que se puede expandir en el futuro
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='perfil_extendido'
    )
    
    # Estadísticas del usuario
    total_recetas = models.PositiveIntegerField(default=0)
    total_seguidores = models.PositiveIntegerField(default=0)
    total_siguiendo = models.PositiveIntegerField(default=0)
    
    # Redes sociales (opcional)
    instagram = models.URLField(blank=True, help_text="Tu perfil de Instagram")
    youtube = models.URLField(blank=True, help_text="Tu canal de YouTube")
    blog_personal = models.URLField(blank=True, help_text="Tu blog de cocina")
    
    # Verificación
    cuenta_verificada = models.BooleanField(
        default=False,
        help_text="Usuario verificado (chef profesional, influencer, etc.)"
    )
    
    class Meta:
        verbose_name = "Perfil Extendido"
        verbose_name_plural = "Perfiles Extendidos"
        
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
