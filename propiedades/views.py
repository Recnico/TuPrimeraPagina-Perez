from django.shortcuts import render, redirect
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm , EditProfileForm , AvatarForm
from .models import Venta , Avatar
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def home(request):
    return render(request, 'propiedades/home.html')

def agregar_corredor(request):
    if request.method == 'POST':
        form = CorredorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CorredorForm()
    return render(request, 'propiedades/form_template.html', {'form': form, 'titulo': 'Agregar Corredor'})

def agregar_arriendo(request):
    if request.method == 'POST':
        form = ArriendoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ArriendoForm()
    return render(request, 'propiedades/form_template.html', {'form': form, 'titulo': 'Agregar Arriendo'})

def agregar_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = VentaForm()
    return render(request, 'propiedades/form_template.html', {'form': form, 'titulo': 'Agregar Venta'})

def buscar_venta(request):
    form = VentaSearchForm(request.GET or None)
    ventas = Venta.objects.all()
    busqueda_realizada = False  # Nueva bandera

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
        # password_form = PasswordChangeForm(request.user) # No necesario aquí
        avatar_form = AvatarForm(instance=avatar_instance) # Para mostrar el avatar actual si existe

    return render(request, 'propiedades/editarPerfil.html', {
        'form': form,
        # 'password_form': password_form, # Ya no se pasa este formulario
        'avatar_form': avatar_form, # Pasamos el formulario del avatar a la plantilla
    })