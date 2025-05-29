# propiedades/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm, EditProfileForm, AvatarForm, ImagenFormSet, UserRegisterForm , BuscarPropiedadForm
from .models import Venta, Avatar, Imagen, Arriendo, Corredor
from django.contrib.auth.forms import UserChangeForm 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login # Import login
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
            messages.success(request, 'Corredor agregado correctamente.')
            return redirect('home')
    else:
        form = CorredorForm()
    return render(request, 'propiedades/agregar_corredor.html', {'form': form})

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


def register_request(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                publicadores_group = Group.objects.get(name='Publicadores')
            except Group.DoesNotExist:
                # Si el grupo no existe, créalo y asigna los permisos necesarios
                publicadores_group = Group.objects.create(name='Publicadores')

                # Obtener los ContentType para tus modelos Venta y Arriendo
                venta_content_type = ContentType.objects.get_for_model(Venta)
                arriendo_content_type = ContentType.objects.get_for_model(Arriendo)

                # Obtener los permisos específicos para Venta y Arriendo
                add_venta = Permission.objects.get(codename='add_venta', content_type=venta_content_type)
                change_venta = Permission.objects.get(codename='change_venta', content_type=venta_content_type)
                delete_venta = Permission.objects.get(codename='delete_venta', content_type=venta_content_type)

                add_arriendo = Permission.objects.get(codename='add_arriendo', content_type=arriendo_content_type)
                change_arriendo = Permission.objects.get(codename='change_arriendo', content_type=arriendo_content_type)
                delete_arriendo = Permission.objects.get(codename='delete_arriendo', content_type=arriendo_content_type)

                # Asignar los permisos al grupo 'Publicadores'
                publicadores_group.permissions.add(add_venta, change_venta, delete_venta, add_arriendo, change_arriendo, delete_arriendo)
                publicadores_group.save()

            # Añadir el usuario al grupo 'Publicadores'
            user.groups.add(publicadores_group)

            messages.success(request, 'Registro exitoso. ¡Ahora puedes iniciar sesión con tu cuenta de publicador!')
            return redirect('login')
        else:
            messages.error(request, 'Hubo errores en el registro. Por favor, corrige los campos.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
# --- Fin vista modificada ---



def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    imagenes_galeria = venta.get_gallery_images()  # Asegúrate de que este método exista en tu modelo Venta
    return render(request, 'propiedades/detalle_venta.html', {'venta': venta, 'imagenes_galeria': imagenes_galeria})

@login_required
def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    # Solo el usuario que publicó la propiedad puede editarla o un superuser
    if request.user != venta.usuario and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar esta propiedad.")
        return redirect('detalle_venta', pk=pk)

    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta)
        formset = ImagenFormSet(request.POST, request.FILES, instance=venta)
        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta_form.save()
                formset.save()

                # Procesa nuevas imágenes subidas durante la edición de venta
                if request.FILES.getlist('gallery_images'):
                    for uploaded_file in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(
                            content_object=venta,
                            imagen=uploaded_file,
                            descripcion=""
                        )
                messages.success(request, 'Propiedad de venta y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la propiedad de venta. Por favor, revisa los datos.')
    else:
        venta_form = VentaForm(instance=venta)
        formset = ImagenFormSet(instance=venta)
    return render(request, 'propiedades/agregar_venta.html', { # Reutiliza la plantilla de agregar_venta
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Editar Venta',
        'is_edit': True,
    })

def detalle_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    imagenes_galeria = arriendo.get_gallery_images() # Asume que este método existe
    return render(request, 'propiedades/detalle_arriendo.html', {'arriendo': arriendo, 'imagenes_galeria': imagenes_galeria})

@login_required
def editar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    # Solo el usuario que publicó la propiedad puede editarla o un superuser
    if request.user != arriendo.usuario and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar esta propiedad.")
        return redirect('detalle_arriendo', pk=pk)

    if request.method == 'POST':
        arriendo_form = ArriendoForm(request.POST, request.FILES, instance=arriendo)
        # Pasa la instancia para que el formset sepa qué imágenes editar/eliminar
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

def buscar_arriendo(request):
    form = BuscarPropiedadForm(request.GET)
    arriendos = Arriendo.objects.all()
    busqueda_realizada = False

    if form.is_valid():
        busqueda_realizada = True
        direccion = form.cleaned_data.get('direccion')
        precio_mensual_min = request.GET.get('precio_mensual_min')  # Accede directamente a request.GET
        precio_mensual_max = request.GET.get('precio_mensual_max')  # Accede directamente a request.GET
        corredor_id = form.cleaned_data.get('corredor')

        if direccion:
            arriendos = arriendos.filter(direccion__icontains=direccion)
        if precio_mensual_min:
            arriendos = arriendos.filter(precio_mensual__gte=precio_mensual_min)
        if precio_mensual_max:
            arriendos = arriendos.filter(precio_mensual__lte=precio_mensual_max)
        if corredor_id:
            arriendos = arriendos.filter(Corredor=corredor_id)

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
        busqueda_realizada = True
        direccion = form.cleaned_data.get('direccion')
        precio_min = form.cleaned_data.get('precio_min')
        precio_max = form.cleaned_data.get('precio_max')
        corredor_id = form.cleaned_data.get('corredor')

        if direccion:
            ventas = ventas.filter(direccion__icontains=direccion)
        if precio_min:
            ventas = ventas.filter(precio__gte=precio_min)
        if precio_max:
            ventas = ventas.filter(precio__lte=precio_max)
        if corredor_id:
            ventas = ventas.filter(Corredor=corredor_id)
            
    return render(request, 'propiedades/buscar_venta.html', {
        'form': form,
        'ventas': ventas,
        'busqueda_realizada': busqueda_realizada
    })

@login_required
def perfil(request):
    return render(request, 'propiedades/perfil.html')

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
    Vista para la página "Acerca de mí".
    """
    return render(request, 'propiedades/about.html')


