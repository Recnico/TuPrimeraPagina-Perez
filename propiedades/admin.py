from django.contrib import admin
from .models import Avatar , Corredor , Venta , Arriendo , Imagen
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html

admin.site.register(Avatar)
admin.site.register(Corredor)

class ImagenInline(GenericTabularInline):
    model = Imagen
    extra = 3
    fields = ['imagen', 'descripcion', 'orden']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('direccion', 'precio', 'Corredor', 'destacada', 'imagen_principal_thumbnail')
    search_fields = ('direccion',)
    list_filter = ('Corredor', 'destacada')

    inlines = [ImagenInline]

    def imagen_principal_thumbnail(self, obj):
        if obj.imagen_principal:
            return format_html(f'<img src="{obj.imagen_principal.url}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />')
        return "No hay imagen"
    imagen_principal_thumbnail.short_description = 'Principal'

@admin.register(Arriendo)
class ArriendoAdmin(admin.ModelAdmin):
    list_display = ('direccion', 'precio_mensual', 'Corredor', 'destacada')
    search_fields = ('direccion',)
    list_filter = ('Corredor', 'destacada')

    inlines = [ImagenInline]