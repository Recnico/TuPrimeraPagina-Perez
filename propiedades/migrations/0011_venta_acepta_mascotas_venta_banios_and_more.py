# Generated by Django 5.2.1 on 2025-06-01 20:17

import ckeditor_uploader.fields
import propiedades.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propiedades', '0010_alter_arriendo_descripcion_alter_avatar_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='acepta_mascotas',
            field=models.BooleanField(default=False, verbose_name='Acepta Mascotas'),
        ),
        migrations.AddField(
            model_name='venta',
            name='banios',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Número de Baños'),
        ),
        migrations.AddField(
            model_name='venta',
            name='descripcion_detallada',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='Proporciona una descripción completa y detallada de la propiedad. Puedes usar formato enriquecido y añadir imágenes.', null=True, verbose_name='Descripción Detallada'),
        ),
        migrations.AddField(
            model_name='venta',
            name='disponible_desde',
            field=models.DateField(blank=True, help_text='Fecha a partir de la cual la propiedad está disponible.', null=True, verbose_name='Disponible Desde'),
        ),
        migrations.AddField(
            model_name='venta',
            name='estacionamientos',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Estacionamientos'),
        ),
        migrations.AddField(
            model_name='venta',
            name='habitaciones',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Número de Habitaciones'),
        ),
        migrations.AddField(
            model_name='venta',
            name='metros_cuadrados',
            field=models.PositiveIntegerField(blank=True, help_text='Superficie total en metros cuadrados.', null=True, verbose_name='Metros Cuadrados'),
        ),
        migrations.AddField(
            model_name='venta',
            name='orientacion',
            field=models.CharField(blank=True, help_text='Ej: Norte, Sur, Oriente, Poniente.', max_length=50, null=True, verbose_name='Orientación'),
        ),
        migrations.AlterField(
            model_name='avatar',
            name='imagen',
            field=models.ImageField(default='avatares/default_avatar.png', upload_to=propiedades.models.avatar_upload_path),
        ),
    ]
