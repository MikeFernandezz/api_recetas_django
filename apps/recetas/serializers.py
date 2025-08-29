from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Categoria, Ingrediente, Receta, RecetaIngrediente,
    Rating, Favorito, ImagenReceta
)

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información básica del usuario
    """
    nombre_completo = serializers.CharField(source='get_nombre_completo', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'nombre_completo', 'avatar', 'nivel_experiencia',
            'pais', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializer para categorías de cocina
    """
    total_recetas = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Categoria
        fields = [
            'id', 'nombre', 'descripcion', 'imagen', 
            'slug', 'activa', 'total_recetas'
        ]
        read_only_fields = ['id', 'total_recetas']


class IngredienteSerializer(serializers.ModelSerializer):
    """
    Serializer para ingredientes
    """
    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre', 'categoria_ingrediente']
        read_only_fields = ['id']


class RecetaIngredienteSerializer(serializers.ModelSerializer):
    """
    Serializer para ingredientes de una receta específica
    """
    ingrediente = IngredienteSerializer(read_only=True)
    ingrediente_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = RecetaIngrediente
        fields = [
            'id', 'ingrediente', 'ingrediente_id', 
            'cantidad', 'opcional'
        ]
        read_only_fields = ['id']


class ImagenRecetaSerializer(serializers.ModelSerializer):
    """
    Serializer para imágenes adicionales de recetas
    """
    class Meta:
        model = ImagenReceta
        fields = [
            'id', 'imagen', 'descripcion', 'orden', 'fecha_subida'
        ]
        read_only_fields = ['id', 'fecha_subida']


class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer para valoraciones de recetas
    """
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Rating
        fields = [
            'id', 'usuario', 'usuario_id', 'puntuacion', 
            'comentario', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def create(self, validated_data):
        """Asigna automáticamente el usuario autenticado"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class RecetaListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listado de recetas
    """
    autor = UsuarioSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    tiempo_total = serializers.IntegerField(read_only=True)
    rating_promedio = serializers.FloatField(read_only=True)
    total_favoritos = serializers.IntegerField(read_only=True)
    es_favorito = serializers.SerializerMethodField()
    
    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'descripcion', 'autor', 'categoria',
            'tiempo_preparacion', 'tiempo_coccion', 'tiempo_total',
            'dificultad', 'porciones', 'imagen_principal',
            'rating_promedio', 'total_favoritos', 'vistas',
            'fecha_creacion', 'es_favorito'
        ]
    
    def get_es_favorito(self, obj):
        """Indica si la receta es favorita del usuario actual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favoritos.filter(usuario=request.user).exists()
        return False


class RecetaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle de recetas
    """
    autor = UsuarioSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    ingredientes_detalle = RecetaIngredienteSerializer(many=True, read_only=True)
    imagenes_adicionales = ImagenRecetaSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    
    # Campos calculados
    tiempo_total = serializers.IntegerField(read_only=True)
    rating_promedio = serializers.FloatField(read_only=True)
    total_favoritos = serializers.IntegerField(read_only=True)
    es_favorito = serializers.SerializerMethodField()
    
    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'descripcion', 'autor', 'categoria',
            'tiempo_preparacion', 'tiempo_coccion', 'tiempo_total',
            'dificultad', 'porciones', 'instrucciones',
            'calorias_por_porcion', 'imagen_principal',
            'ingredientes_detalle', 'imagenes_adicionales',
            'ratings', 'rating_promedio', 'total_favoritos',
            'vistas', 'publicada', 'destacada',
            'fecha_creacion', 'fecha_actualizacion', 'es_favorito'
        ]
        read_only_fields = [
            'id', 'autor', 'vistas', 'fecha_creacion', 
            'fecha_actualizacion'
        ]
    
    def get_es_favorito(self, obj):
        """Indica si la receta es favorita del usuario actual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favoritos.filter(usuario=request.user).exists()
        return False


class RecetaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar recetas
    """
    ingredientes = RecetaIngredienteSerializer(many=True, write_only=True, required=False)
    imagenes = ImagenRecetaSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Receta
        fields = [
            'titulo', 'descripcion', 'categoria',
            'tiempo_preparacion', 'tiempo_coccion',
            'dificultad', 'porciones', 'instrucciones',
            'calorias_por_porcion', 'imagen_principal',
            'ingredientes', 'imagenes'
        ]
    
    def create(self, validated_data):
        """Crear receta con ingredientes e imágenes"""
        ingredientes_data = validated_data.pop('ingredientes', [])
        imagenes_data = validated_data.pop('imagenes', [])
        
        # Asignar autor automáticamente
        validated_data['autor'] = self.context['request'].user
        
        # Crear la receta
        receta = Receta.objects.create(**validated_data)
        
        # Crear ingredientes
        for ingrediente_data in ingredientes_data:
            RecetaIngrediente.objects.create(receta=receta, **ingrediente_data)
        
        # Crear imágenes adicionales
        for imagen_data in imagenes_data:
            ImagenReceta.objects.create(receta=receta, **imagen_data)
        
        return receta
    
    def update(self, instance, validated_data):
        """Actualizar receta con ingredientes e imágenes"""
        ingredientes_data = validated_data.pop('ingredientes', None)
        imagenes_data = validated_data.pop('imagenes', None)
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar ingredientes si se proporcionan
        if ingredientes_data is not None:
            instance.ingredientes_detalle.all().delete()
            for ingrediente_data in ingredientes_data:
                RecetaIngrediente.objects.create(receta=instance, **ingrediente_data)
        
        # Actualizar imágenes si se proporcionan
        if imagenes_data is not None:
            instance.imagenes_adicionales.all().delete()
            for imagen_data in imagenes_data:
                ImagenReceta.objects.create(receta=instance, **imagen_data)
        
        return instance


class FavoritoSerializer(serializers.ModelSerializer):
    """
    Serializer para favoritos
    """
    receta = RecetaListSerializer(read_only=True)
    receta_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Favorito
        fields = ['id', 'receta', 'receta_id', 'fecha_agregado']
        read_only_fields = ['id', 'fecha_agregado']
    
    def create(self, validated_data):
        """Asigna automáticamente el usuario autenticado"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class EstadisticasRecetaSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de recetas
    """
    total_recetas = serializers.IntegerField()
    total_publicadas = serializers.IntegerField()
    total_borradores = serializers.IntegerField()
    receta_mas_vista = serializers.CharField()
    receta_mejor_valorada = serializers.CharField()
    categoria_mas_popular = serializers.CharField()
