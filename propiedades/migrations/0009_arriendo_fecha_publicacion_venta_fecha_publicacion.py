# Generated by Django 5.2.1 on 2025-05-31 01:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propiedades', '0008_merge_20250523_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='arriendo',
            name='fecha_publicacion',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='fecha_publicacion',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
