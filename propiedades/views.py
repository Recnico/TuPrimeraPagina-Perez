# propiedades/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm, EditProfileForm, AvatarForm, ImagenFormSet, UserRegisterForm , BuscarPropiedadForm
from .models import Venta, Avatar, Imagen, Arriendo, Corredor
from django.contrib.auth.forms import UserChangeForm 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, login 
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm 
from django.contrib.auth import update_session_auth_hash 
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


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
            messages.success(request, 'Corredor agregado exitosamente.')
            return redirect('home')  
    else:
        form = CorredorForm()
    return render(request, 'propiedades/agregar_corredor.html', {'form': form})

@login_required
def agregar_arriendo(request):
    if request.method == 'POST':
        arriendo_form = ArriendoForm(request.POST, request.FILES)
        formset = ImagenFormSet(request.POST, request.FILES)
        if arriendo_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                arriendo = arriendo_form.save(commit=False)
                arriendo.usuario = request.user  # Asigna el usuario actual
                arriendo.save()
                
                for form in formset:
                    if form.cleaned_data:
                        imagen = form.save(commit=False)
                        imagen.content_object = arriendo
                        imagen.save()
                messages.success(request, 'Propiedad de arriendo y galería de imágenes guardadas correctamente.')
                return redirect('detalle_arriendo', pk=arriendo.pk)
        else:
            messages.error(request, 'Hubo errores al guardar la propiedad de arriendo. Por favor, revisa los datos.')
    else:
        arriendo_form = ArriendoForm()
        formset = ImagenFormSet()
    return render(request, 'propiedades/agregar_arriendo.html', {
        'arriendo_form': arriendo_form,
        'formset': formset,
        'titulo': 'Agregar Nuevo Arriendo',
        'is_edit': False,
    })

@login_required
def agregar_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES)
        formset = ImagenFormSet(request.POST, request.FILES)
        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = venta_form.save(commit=False)
                venta.usuario = request.user  # Asigna el usuario actual
                venta.save()
                
                for form in formset:
                    if form.cleaned_data:
                        imagen = form.save(commit=False)
                        imagen.content_object = venta
                        imagen.save()
                messages.success(request, 'Propiedad de venta y galería de imágenes guardadas correctamente.')
                return redirect('detalle_venta', pk=venta.pk)
        else:
            messages.error(request, 'Hubo errores al guardar la propiedad de venta. Por favor, revisa los datos.')
    else:
        venta_form = VentaForm()
        formset = ImagenFormSet()
    return render(request, 'propiedades/agregar_venta.html', {
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Agregar Nueva Venta',
        'is_edit': False,
    })

def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    imagenes = venta.get_gallery_images()
    return render(request, 'propiedades/detalle_venta.html', {'venta': venta, 'imagenes': imagenes})

@login_required
def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    # Solo permitir la edición si el usuario es el creador de la propiedad o es staff/superuser
    if venta.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para editar esta propiedad.')
        return redirect('detalle_venta', pk=pk) # O a la página de perfil, etc.

    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta)
        formset = ImagenFormSet(request.POST, request.FILES, instance=venta)
        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta_form.save()
                formset.save()

                # --- NUEVA LÓGICA: Procesa nuevas imágenes subidas durante la edición de venta ---
                if request.FILES.getlist('gallery_images'):
                    for uploaded_file in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(
                            content_object=venta,
                            imagen=uploaded_file,
                            descripcion=""
                        )
                # --- FIN NUEVA LÓGICA ---

            messages.success(request, 'Propiedad de venta y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la propiedad de venta. Por favor, revisa los datos.')
    else:
        venta_form = VentaForm(instance=venta)
        formset = ImagenFormSet(instance=venta) # Pasa la instancia de la venta al formset

    return render(request, 'propiedades/agregar_venta.html', { # Reutiliza la plantilla de agregar_venta
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Editar Venta',
        'is_edit': True,
    })

def detalle_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    imagenes = arriendo.get_gallery_images()
    return render(request, 'propiedades/detalle_arriendo.html', {'arriendo': arriendo, 'imagenes': imagenes})

@login_required
def editar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)

    # Solo permitir la edición si el usuario es el creador de la propiedad o es staff/superuser
    if arriendo.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para editar esta propiedad.')
        return redirect('detalle_arriendo', pk=pk) # O a la página de perfil, etc.

    if request.method == 'POST':
        arriendo_form = ArriendoForm(request.POST, request.FILES, instance=arriendo)
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

# Nuevas vistas para eliminar propiedades

@login_required
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    # Solo permitir la eliminación si el usuario es el creador de la propiedad o es staff/superuser
    if venta.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para eliminar esta propiedad.')
        return redirect('detalle_venta', pk=pk)

    if request.method == 'POST':
        venta.delete()
        messages.success(request, 'La propiedad de venta ha sido eliminada exitosamente.')
        return redirect('perfil') # Redirige al perfil después de eliminar
    
    return render(request, 'propiedades/confirmar_eliminar.html', {'objeto': venta, 'tipo': 'venta'})

@login_required
def eliminar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)

    # Solo permitir la eliminación si el usuario es el creador de la propiedad o es staff/superuser
    if arriendo.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para eliminar esta propiedad.')
        return redirect('detalle_arriendo', pk=pk)

    if request.method == 'POST':
        arriendo.delete()
        messages.success(request, 'La propiedad de arriendo ha sido eliminada exitosamente.')
        return redirect('perfil') # Redirige al perfil después de eliminar

    return render(request, 'propiedades/confirmar_eliminar.html', {'objeto': arriendo, 'tipo': 'arriendo'})


def buscar_arriendo(request):
    form = BuscarPropiedadForm(request.GET)
    arriendos = Arriendo.objects.all()
    busqueda_realizada = False

    if form.is_valid():
        direccion = form.cleaned_data.get('direccion')
        if direccion:
            arriendos = arriendos.filter(direccion__icontains=direccion)
            busqueda_realizada = True
    
    return render(request, 'propiedades/buscar_arriendo.html', {
        'form': form,
        'arriendos': arriendos,
        'busqueda_realizada': busqueda_realizada
    })

def buscar_venta(request):
    form = VentaSearchForm(request.GET)
    ventas = Venta.objects.all()
    busqueda_realizada = False

    if form.is_valid():
        direccion = form.cleaned_data.get('direccion')
        precio_min = form.cleaned_data.get('precio_min')
        precio_max = form.cleaned_data.get('precio_max')
        corredor = form.cleaned_data.get('corredor')

        if direccion:
            ventas = ventas.filter(direccion__icontains=direccion)
            busqueda_realizada = True
        if precio_min is not None:
            ventas = ventas.filter(precio__gte=precio_min)
            busqueda_realizada = True
        if precio_max is not None:
            ventas = ventas.filter(precio__lte=precio_max)
            busqueda_realizada = True
        if corredor:
            ventas = ventas.filter(Corredor=corredor)
            busqueda_realizada = True
   
    return render(request, 'propiedades/buscar_venta.html', {
        'form': form,
        'ventas': ventas,
        'busqueda_realizada': busqueda_realizada
    })

@login_required
def perfil(request):
    # Obtener las propiedades de venta y arriendo publicadas por el usuario
    ventas_usuario = Venta.objects.filter(usuario=request.user)
    arriendos_usuario = Arriendo.objects.filter(usuario=request.user)

    context = {
        'ventas_usuario': ventas_usuario,
        'arriendos_usuario': arriendos_usuario,
    }
    return render(request, 'propiedades/perfil.html', context)

@login_required
def editarPerfil(request):
    User = get_user_model()
    
    # Manejo del formulario de edición de perfil
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        avatar_form = AvatarForm(request.POST, request.FILES, instance=request.user.avatar if hasattr(request.user, 'avatar') else None)

        if form.is_valid() and avatar_form.is_valid():
            form.save()
            avatar = avatar_form.save(commit=False)
            avatar.user = request.user
            avatar.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = EditProfileForm(instance=request.user)
        avatar_form = AvatarForm(instance=request.user.avatar if hasattr(request.user, 'avatar') else None)

    return render(request, 'propiedades/editarPerfil.html', {'form': form, 'avatar_form': avatar_form})

def about(request):
    """
    Vistas  la página "Acerca de mí".u
    """
    return render(request, 'propiedades/about.html')


def register_request(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asigna el usuario al grupo 'Inmobiliario' si existe
            inmobiliario_group, created = Group.objects.get_or_create(name='Inmobiliario')
            user.groups.add(inmobiliario_group)
            login(request, user)
            messages.success(request, "Registro exitoso.")
            return redirect("home")
        messages.error(request, "Registro fallido. Información inválida.")
    form = UserRegisterForm()
    return render(request, "propiedades/register.html", {"register_form": form})