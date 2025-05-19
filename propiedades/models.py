from django.db import models

from django.db import models

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