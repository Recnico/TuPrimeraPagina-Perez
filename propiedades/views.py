# propiedades/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm, EditProfileForm, AvatarForm, ImagenFormSet
from .models import Venta, Avatar, Imagen, Arriendo, Corredor
from django.contrib.auth.forms import UserChangeForm # No parece usarse directamente, pero la importación está bien
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm # No parece usarse directamente
from django.contrib.auth import update_session_auth_hash # No parece usarse directamente
from django.db import transaction

def home(request):
    ventas_destacadas = Venta.objects.filter(destacada=True)[:3]
    arriendos_destacados = Arriendo.objects.filter(destacada=True)[:3]

    context = {
        'ventas_destacadas': ventas_destacadas,
        'arriendos_destacados': arriendos_destacados,
    }
    return render(request, 'propiedades/home.html', context)

@login_required
def agregar_corredor(request):
    if request.method == 'POST':
        form = CorredorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Corredor agregado correctamente.')
            return redirect('home')
    else:
        form = CorredorForm()
    return render(request, 'propiedades/form_template.html', {'form': form, 'titulo': 'Agregar Corredor'})

@login_required
def agregar_arriendo(request):
    if request.method == 'POST':
        # arriendo_form para los campos del arriendo
        arriendo_form = ArriendoForm(request.POST, request.FILES)

        if arriendo_form.is_valid():
            arriendo_instance = arriendo_form.save(commit=False)
            arriendo_instance.usuario = request.user # Asigna el usuario logueado
            
            with transaction.atomic():
                arriendo_instance.save() # Guarda la instancia de Arriendo para obtener el PK

                # Lógica para procesar múltiples imágenes para arriendo
                # Asumiendo que también tienes un input `name="gallery_images"` en agregar_arriendo.html
                if request.FILES.getlist('gallery_images'):
                    for uploaded_file in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(
                            content_object=arriendo_instance,
                            imagen=uploaded_file,
                            descripcion="" # Puedes dejarla vacía o generar una por defecto
                        )

                messages.success(request, 'Arriendo y galería de imágenes agregados correctamente.')
                return redirect('detalle_arriendo', pk=arriendo_instance.pk) # Redirige al detalle del arriendo
        else:
            messages.error(request, 'Hubo errores en los datos del arriendo. Por favor, revisa los datos.')
            
    else: # GET request
        arriendo_form = ArriendoForm()

    return render(request, 'propiedades/agregar_arriendo.html', { # Asegúrate de que esta plantilla existe
        'arriendo_form': arriendo_form,
        'titulo': 'Agregar Arriendo con Galería',
        'is_edit': False,
    })


@login_required
def agregar_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES)
        
        if venta_form.is_valid():
            venta_instance = venta_form.save(commit=False)
            venta_instance.usuario = request.user 
            
            with transaction.atomic():
                venta_instance.save() # Guarda la instancia de Venta para obtener el PK
                
                # --- NUEVA LÓGICA: Procesa las imágenes subidas por el input 'multiple' ---
                # 'gallery_images' es el 'name' del input file en el HTML que permite múltiples selecciones
                if request.FILES.getlist('gallery_images'): 
                    for uploaded_file in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(
                            content_object=venta_instance, # Asigna la imagen a la venta recién creada
                            imagen=uploaded_file,
                            descripcion="" # Puedes dejarla vacía o generar una por defecto
                        )
                # --- FIN NUEVA LÓGICA ---
                
                messages.success(request, '¡Venta y galería de imágenes agregadas correctamente!')
                return redirect('detalle_venta', pk=venta_instance.pk)
        else:
            messages.error(request, 'Hubo errores en los datos de la venta. Por favor, revisa los datos.')
            
        # Si la venta_form no es válida, re-renderizamos la plantilla con los errores.
        # No hay necesidad de instanciar formset para las nuevas imágenes aquí.
        # El formset solo se usa para imágenes ya existentes en la edición.
    else: # GET request (cuando se carga la página por primera vez)
        venta_form = VentaForm()
        # En la vista de agregar, no pasamos el formset para la carga inicial de imágenes.
        # El formset se usará solo en la vista de edición para mostrar/eliminar imágenes existentes.
        
    return render(request, 'propiedades/agregar_venta.html', { 
        'venta_form': venta_form,
        # 'formset': formset, # Ya no se pasa el formset para AGREGAR
        'titulo': 'Agregar Venta con Galería',
        'is_edit': False, # Indica a la plantilla que no estamos en modo edición
    })

# Nueva vista para ver los detalles de una Venta
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'propiedades/detalle_venta.html', {'venta': venta})

def detalle_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    return render(request, 'propiedades/detalle_arriendo.html', {'arriendo': arriendo})
def buscar_arriendo(request):
    # Aquí puedes crear un formulario de búsqueda para arriendos, similar a VentaSearchForm
    # Si no tienes uno, puedes dejarlo simple por ahora.
    
    # Supongamos que tienes un ArriendoSearchForm en forms.py, si no, puedes crear uno básico
    # from .forms import ArriendoSearchForm # Descomentar si lo creas
    
    # form = ArriendoSearchForm(request.GET or None) # Descomentar y usar tu form de búsqueda
    arriendos = Arriendo.objects.all() # Obtener todos los arriendos inicialmente
    busqueda_realizada = False

    # if form.is_valid(): # Si usas un formulario de búsqueda
    #     busqueda_realizada = True
    #     # Aquí iría la lógica para filtrar los arriendos según los parámetros del formulario
    #     # Ejemplo:
    #     # direccion = form.cleaned_data.get('direccion')
    #     # if direccion:
    #     #     arriendos = arriendos.filter(direccion__icontains=direccion)
    #     # ... y otros filtros como precio, habitaciones, etc.
    
    context = {
        # 'form': form, # Si usas un formulario de búsqueda
        'arriendos': arriendos,
        'busqueda_realizada': busqueda_realizada,
    }
    return render(request, 'propiedades/buscar_arriendo.html', context)


def buscar_venta(request):
    form = VentaSearchForm(request.GET or None)
    ventas = Venta.objects.all()
    busqueda_realizada = False 

    if form.is_valid():
        busqueda_realizada = True
        direccion = form.cleaned_data.get('direccion')
        precio_min = form.cleaned_data.get('precio_min')
        precio_max = form.cleaned_data.get('precio_max')
        corredor = form.cleaned_data.get('corredor')

        if direccion:
            ventas = ventas.filter(direccion__icontains=direccion)
        if precio_min is not None:
            ventas = ventas.filter(precio__gte=precio_min)
        if precio_max is not None:
            ventas = ventas.filter(precio__lte=precio_max)
        if corredor:
            ventas = ventas.filter(Corredor=corredor)

    return render(request, 'propiedades/buscar_venta.html', {'form': form, 'ventas': ventas, 'busqueda_realizada': busqueda_realizada})

def perfil(request):
    return render(request, 'propiedades/perfil.html')


@login_required
def editarPerfil(request):
    try:
        avatar_instance = request.user.avatar 
    except Avatar.DoesNotExist:
        avatar_instance = None

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        
        avatar_form = AvatarForm(request.POST, request.FILES, instance=avatar_instance)

        profile_updated = False
        avatar_updated = False

        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            profile_updated = True

        if avatar_form.is_valid():
            avatar_obj = avatar_form.save(commit=False)
            avatar_obj.user = request.user
            avatar_obj.save()
            messages.success(request, 'Tu avatar ha sido actualizado correctamente.')
            avatar_updated = True
        elif request.FILES: 
            messages.error(request, 'Hubo un error al subir el avatar. Inténtalo de nuevo.')
            
        if profile_updated or avatar_updated:
            return redirect('perfil')

    else:
        form = EditProfileForm(instance=request.user)
        avatar_form = AvatarForm(instance=avatar_instance)

    return render(request, 'propiedades/editarPerfil.html', {
        'form': form,
        'avatar_form': avatar_form,
    })

@login_required
def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    # Lógica de permisos: Solo el creador o un superusuario/admin puede editar
    if not (request.user == venta.usuario or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para editar esta propiedad.')
        return redirect('detalle_venta', pk=venta.pk)

    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta)
        # Aquí SÍ usamos el formset para gestionar las imágenes EXISTENTES (editar descripción, orden, eliminar)
        formset = ImagenFormSet(request.POST, request.FILES, instance=venta)

        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta_form.save() # Guarda los cambios en la Venta

                # Guarda los cambios y eliminaciones del formset para imágenes existentes
                formset.save() 

                # --- NUEVA LÓGICA: Procesa nuevas imágenes subidas durante la edición (campo 'gallery_images') ---
                if request.FILES.getlist('gallery_images'): 
                    for uploaded_file in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(
                            content_object=venta, # Asigna la imagen a la venta que se está editando
                            imagen=uploaded_file,
                            descripcion="" 
                        )
                # --- FIN NUEVA LÓGICA ---
            
            messages.success(request, 'Venta y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la venta. Por favor, revisa los datos.')
    else: # GET request (cuando se carga la página de edición)
        venta_form = VentaForm(instance=venta)
        # Pasa el formset para que se muestren las imágenes existentes para editar/eliminar
        formset = ImagenFormSet(instance=venta) 

    return render(request, 'propiedades/agregar_venta.html', { # Reutilizamos la plantilla
        'venta_form': venta_form,
        'formset': formset, # Pasa el formset para que se muestren las imágenes existentes
        'titulo': 'Editar Venta',
        'is_edit': True, # Indica a la plantilla que estamos en modo edición
    })

@login_required
def editar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    if not (request.user == arriendo.usuario or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para editar esta propiedad de arriendo.')
        return redirect('detalle_arriendo', pk=arriendo.pk)

    if request.method == 'POST':
        arriendo_form = ArriendoForm(request.POST, request.FILES, instance=arriendo)
        # Asumiendo que ImagenFormSet también puede manejar instancias de Arriendo (por GenericForeignKey)
        formset = ImagenFormSet(request.POST, request.FILES, instance=arriendo) 

        if arriendo_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                arriendo_form.save()
                formset.save()

                # --- NUEVA LÓGICA: Procesa nuevas imágenes subidas durante la edición de arriendo ---
                if request.FILES.getlist('gallery_images'):
                    for uploaded_file in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(
                            content_object=arriendo,
                            imagen=uploaded_file,
                            descripcion=""
                        )
                # --- FIN NUEVA LÓGICA ---

            messages.success(request, 'Propiedad de arriendo y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_arriendo', pk=arriendo.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la propiedad de arriendo. Por favor, revisa los datos.')
    else:
        arriendo_form = ArriendoForm(instance=arriendo)
        formset = ImagenFormSet(instance=arriendo)

    return render(request, 'propiedades/agregar_arriendo.html', { # Reutiliza la plantilla de agregar_arriendo
        'arriendo_form': arriendo_form,
        'formset': formset,
        'titulo': 'Editar Arriendo',
        'is_edit': True,
    })

def about(request):
    """
    Vistas  la página "Acerca de mí".u
    """
    return render(request, 'propiedades/about.html')