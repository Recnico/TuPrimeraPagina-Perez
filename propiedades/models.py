from django.db import models
from django.contrib.auth.models import User
import os

class Corredor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    direccion = models.CharField(max_length=200)
    precio = models.IntegerField()
    Corredor = models.ForeignKey(Corredor, on_delete=models.CASCADE)

    def __str__(self):
        return self.direccion

class Arriendo(models.Model):
    direccion = models.CharField(max_length=200)
    precio_mensual = models.IntegerField()
    Corredor = models.ForeignKey(Corredor, on_delete=models.CASCADE)

    def __str__(self):
        return self.direccion
    


def avatar_upload_path(instance, filename):
    base_name, ext = os.path.splitext(filename)
    clean_base_name = base_name.split('.')[0] if '.' in base_name else base_name

    return f'avatares/{clean_base_name}{ext.lower()}'

    
class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='avatar')
    imagen = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.imagen.name if self.imagen else 'Sin imagen'}"