# propiedades/views.py

from django.shortcuts import render, redirect, get_object_or_404 # Agregamos get_object_or_404
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm , EditProfileForm , AvatarForm, ImagenFormSet # Importa ImagenFormSet
from .models import Venta , Avatar, Imagen , Arriendo
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db import transaction 

def home(request):
    
    ventas_destacadas = Venta.objects.filter(destacada=True)[:3]

    
    arriendos_destacados = Arriendo.objects.filter(destacada=True)[:3]

    context = {
        'ventas_destacadas': ventas_destacadas,
        'arriendos_destacados': arriendos_destacados,
    }
    return render(request, 'propiedades/home.html', context)


def agregar_corredor(request):
    if request.method == 'POST':
        form = CorredorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Corredor agregado correctamente.') # Mensaje de éxito
            return redirect('home')
    else:
        form = CorredorForm()
    return render(request, 'propiedades/form_template.html', {'form': form, 'titulo': 'Agregar Corredor'})

def agregar_arriendo(request):
    if request.method == 'POST':
        form = ArriendoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arriendo agregado correctamente.') # Mensaje de éxito
            return redirect('home')
    else:
        form = ArriendoForm()
    return render(request, 'propiedades/form_template.html', {'form': form, 'titulo': 'Agregar Arriendo'})


def agregar_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES) # Pasa request.FILES para imagen_principal
        
        # Primero, intenta validar el formulario de Venta.
        if venta_form.is_valid():
            # No guardamos la venta todavía (commit=False) porque necesitamos su instancia
            # para el formset de imágenes, pero aún no tiene un PK si es nueva.
            # La guardaremos dentro de la transacción atómica si todo lo demás es válido.
            venta_instance = venta_form.save(commit=False)
            
            # Instancia el formset con los datos POST y FILES, y lo más importante:
            # Pasa la instancia de la Venta como 'instance' al formset.
            # Esto es crucial para que generic_inlineformset_factory sepa a qué objeto relacionar las imágenes.
            formset = ImagenFormSet(request.POST, request.FILES, instance=venta_instance) 

            # Ahora, valida el formset.
            if formset.is_valid():
                # Si ambos formularios son válidos, procedemos a guardar en una transacción atómica.
                with transaction.atomic():
                    venta_instance.save() # Guarda la instancia de Venta (ahora tiene un PK)

                    # El método save() del generic_inlineformset_factory:
                    # 1. Asigna automáticamente content_type y object_id (el PK de venta_instance) a cada imagen.
                    # 2. Guarda las nuevas imágenes.
                    # 3. Actualiza las imágenes existentes.
                    # 4. Elimina las imágenes marcadas para eliminación.
                    formset.save() # Guarda las imágenes de la galería

                messages.success(request, '¡Venta y galería de imágenes agregadas correctamente!')
                return redirect('detalle_venta', pk=venta_instance.pk)
            else:
                # Si el formset NO es válido, se mostrarán los errores del formset.
                messages.error(request, 'Hubo errores en las imágenes de la galería. Por favor, revisa los datos.')
        else:
            # Si el formulario de Venta NO es válido, se mostrarán sus errores.
            messages.error(request, 'Hubo errores en los datos de la venta. Por favor, revisa los datos.')
        
        # Si llegamos aquí (algún formulario no fue válido en el POST),
        # re-instanciamos los formularios con los datos POST y FILES
        # para que se muestren los errores en la plantilla.
        # Es importante re-instanciar el formset con la instancia de venta_instance,
        # incluso si la venta no fue válida, para que los errores se muestren correctamente.
        if 'venta_instance' not in locals(): # Si venta_instance no se creó (ej. venta_form no válido)
             venta_instance = None # O podrías intentar obtenerla si es una edición
        formset = ImagenFormSet(request.POST, request.FILES, instance=venta_instance)


    else: # GET request (cuando el usuario accede a la página por primera vez)
        venta_form = VentaForm()
        formset = ImagenFormSet() # Crea un formset vacío para nuevas imágenes

    # Renderiza la plantilla con los formularios (vacíos en GET, o con datos y errores en POST si no fue válido)
    return render(request, 'propiedades/agregar_venta.html', { 
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Agregar Venta con Galería',
    })

# Nueva vista para ver los detalles de una Venta
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    # Las imágenes de la galería se obtienen con venta.get_gallery_images()
    return render(request, 'propiedades/detalle_venta.html', {'venta': venta})


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