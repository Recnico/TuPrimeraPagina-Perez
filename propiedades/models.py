from django.db import models
from django.contrib.auth.models import User # Asegúrate de importar User
import os
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor_uploader.fields import RichTextUploadingField

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
    destacada = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas_publicadas')
    fecha_publicacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.direccion

    def get_gallery_images(self):
        return Imagen.objects.filter(
        content_type=ContentType.objects.get_for_model(self),
        object_id=self.id
    )


class Arriendo(models.Model):
    Corredor = models.ForeignKey(Corredor, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=0)
    descripcion = RichTextUploadingField(blank=True, null=True) # Usa RichTextUploadingField para subir imágenes
    imagen_principal = models.ImageField(upload_to='arriendos/', blank=True, null=True)
    destacada = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='arriendos_publicados')
    fecha_publicacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.direccion

    def get_gallery_images(self):
        return Imagen.objects.filter(
        content_type=ContentType.objects.get_for_model(self),
        object_id=self.id
    )
    
class Imagen(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    imagen = models.ImageField(upload_to=property_image_upload_path)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    orden = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['orden']

    def __str__(self):
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