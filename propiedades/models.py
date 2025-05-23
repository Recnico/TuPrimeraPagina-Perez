from django.db import models
from django.contrib.auth.models import User
import os
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

def avatar_upload_path(instance, filename):
    base_name, ext = os.path.splitext(filename)
    clean_base_name = base_name.split('.')[0] if '.' in base_name else base_name

    return f'avatares/{clean_base_name}{ext.lower()}'

def property_image_upload_path(instance, filename):
    return f'galeria_propiedades/{filename}'


class Corredor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    class Meta: 
        verbose_name = "Corredor"
        verbose_name_plural = "Corredores"

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    direccion = models.CharField(max_length=200)
    precio = models.IntegerField()
    imagen_principal = models.ImageField(upload_to='ventas_pics/', null=True, blank=True)
    Corredor = models.ForeignKey(Corredor, on_delete=models.CASCADE)

    def __str__(self):
        return self.direccion
    
     # Método para obtener las imágenes de la galería usando el modelo Imagen genérico
    def get_gallery_images(self):
        return Imagen.objects.filter(content_type=ContentType.objects.get_for_model(self), object_id=self.id)


class Arriendo(models.Model):
    direccion = models.CharField(max_length=200)
    precio_mensual = models.IntegerField()
    Corredor = models.ForeignKey(Corredor, on_delete=models.CASCADE)

    def __str__(self):
        return self.direccion
    
class Imagen(models.Model):
    # Campos para Generic Foreign Key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') # Este campo es solo para facilitar el acceso Python

    imagen = models.ImageField(upload_to=property_image_upload_path) # Usamos la función de subida genérica
    descripcion = models.CharField(max_length=255, blank=True, null=True) # Opcional: Descripción para cada imagen
    orden = models.PositiveIntegerField(default=0, blank=True, null=True) # Para ordenar las imágenes en la galería

    class Meta:
        ordering = ['orden'] # Ordenar las imágenes por este campo

    def __str__(self):
        # Asegúrate de que content_object no sea None antes de intentar acceder a sus atributos
        if self.content_object:
            return f"Imagen para {self.content_object} ({self.id})"
        return f"Imagen genérica ({self.id})"

    
class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='avatar')
    imagen = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)

    class Meta:
        verbose_name = "Avatar"
        verbose_name_plural = "Avatar" 

    def __str__(self):
        return f"{self.user.username} - {self.imagen.name if self.imagen else 'Sin imagen'}"