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
        # IMPORTANTE: No uses prefix si es el único formset en la página de agregar.
        # Si usaras varios formsets del mismo tipo (ImagenFormSet), entonces sí.
        formset = ImagenFormSet(request.POST, request.FILES)
        if arriendo_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                arriendo = arriendo_form.save(commit=False)
                arriendo.usuario = request.user  # Asigna el usuario actual
                arriendo.save()

                # --- CORRECCIÓN CLAVE AQUÍ ---
                # Guarda las instancias del formset que son válidas y tienen datos.
                # formset.save(commit=False) devuelve una lista de instancias
                # de Imagen válidas, sin guardar todavía.
                imagenes = formset.save(commit=False)
                for imagen in imagenes:
                    imagen.content_object = arriendo
                    imagen.save()
                # Si el formset tiene 'can_delete=True', también puedes procesar las eliminaciones
                # formset.save_m2m() si tuvieras ManyToMany fields en Imagen, pero no es el caso.
                # --- FIN CORRECCIÓN ---

                messages.success(request, 'Propiedad de arriendo y galería de imágenes guardadas correctamente.')
                return redirect('detalle_arriendo', pk=arriendo.pk)
        else:
            messages.error(request, 'Hubo errores al guardar la propiedad de arriendo. Por favor, revisa los datos.')
            # Para depurar, puedes imprimir los errores:
            # print("Errores del formulario de arriendo:", arriendo_form.errors)
            # print("Errores del formset:", formset.errors)
            # for f in formset:
            #     print(f"Errores del formulario de imagen {f.prefix}: {f.errors}")

    else:
        arriendo_form = ArriendoForm()
        formset = ImagenFormSet()
    return render(request, 'propiedades/agregar_arriendo.html', {
        'arriendo_form': arriendo_form,
        'formset': formset,
        'titulo': 'Agregar Nuevo Arriendo',
        'is_edit': False,
    })

# @login_required # Puedes aplicar este decorador si solo usuarios logueados pueden agregar/editar
def agregar_o_editar_venta(request, pk=None):
    venta_instance = None
    is_edit = False

    if pk: # Si se proporciona un PK, estamos en modo edición
        venta_instance = get_object_or_404(Venta, pk=pk)
        is_edit = True
    
    # Inicializa el formulario principal
    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta_instance)
        
        # Inicializa el formset SÓLO si estamos editando (para gestionar imágenes existentes)
        formset = None
        if is_edit:
            formset = ImagenFormSet(request.POST, request.FILES, instance=venta_instance)
        
        # Bandera para saber si todo es válido
        all_forms_valid = False

        if venta_form.is_valid():
            if is_edit: # Si estamos editando, también validamos el formset
                if formset and formset.is_valid(): # Asegurarse de que el formset fue inicializado y es válido
                    all_forms_valid = True
                elif not formset: # Este caso no debería pasar si is_edit es True
                    messages.error(request, 'Error interno: el formset no pudo ser inicializado para edición.')
            else: # Si estamos agregando, solo necesitamos que venta_form sea válido
                all_forms_valid = True
        
        if all_forms_valid:
            with transaction.atomic():
                # Guarda el formulario principal
                venta = venta_form.save(commit=False)
                if not is_edit: # Solo asigna el usuario si es una nueva venta
                    venta.usuario = request.user
                venta.save()

                # Procesa el formset para imágenes existentes (solo si estamos editando)
                if is_edit and formset:
                    # Guarda las imágenes modificadas/nuevas del formset
                    imagenes_formset = formset.save(commit=False)
                    for imagen in imagenes_formset:
                        imagen.content_object = venta
                        imagen.save()
                    # Elimina las imágenes marcadas para borrar
                    for imagen_to_delete in formset.deleted_objects:
                        imagen_to_delete.delete()

                # Procesa las nuevas imágenes del campo 'gallery_images' (siempre que se suban)
                if 'gallery_images' in request.FILES:
                    for f in request.FILES.getlist('gallery_images'):
                        # Aquí puedes agregar validaciones adicionales para 'f' si es necesario
                        # Por ejemplo, verificar el tamaño o tipo de archivo antes de guardar
                        Imagen.objects.create(content_object=venta, imagen=f)

            messages.success(request, 'Propiedad y galería de imágenes guardadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk) # Redirige a la vista de detalle
        else:
            # --- CÓDIGO DE DEPURACIÓN (MANTENLO PARA VER ERRORES EN LA TERMINAL) ---
            print("--- ERRORES DE VALIDACIÓN ---")
            if venta_form.errors:
                print("Errores en VentaForm:", venta_form.errors.as_json())
            if formset and formset.errors: # Si el formset fue inicializado y tiene errores
                print("Errores generales en Formset:", formset.errors)
                for i, form in enumerate(formset):
                    if form.errors:
                        print(f"Errores en el formulario de imagen #{i}:", form.errors.as_json())
            print("--- FIN DE ERRORES ---")
            # --- FIN CÓDIGO DE DEPURACIÓN ---
            
            messages.error(request, 'Hubo errores al guardar la propiedad. Por favor, revisa los datos.')

    else: # GET request (para mostrar el formulario por primera vez)
        venta_form = VentaForm(instance=venta_instance)
        # Inicializa el formset SOLO si estamos editando
        formset = ImagenFormSet(instance=venta_instance) if is_edit else None

    context = {
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Editar Venta' if is_edit else 'Agregar Nueva Venta',
        'is_edit': is_edit, # Pasar la bandera is_edit a la plantilla
    }
    return render(request, 'propiedades/agregar_venta.html', context)


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
        return redirect('detalle_venta', pk=pk)

    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta)
        formset = ImagenFormSet(request.POST, request.FILES, instance=venta)
        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta_form.save()
                # formset.save() ya guarda las instancias existentes, elimina las marcadas para eliminación
                # y guarda las nuevas válidas.
                # No necesitas el bucle manual si usas formset.save() sin commit=False aquí.
                formset.save() # Guarda y actualiza las instancias de Imagen

                # La "NUEVA LÓGICA" que tenías aquí para 'gallery_images' duplicaba el propósito del formset.
                # Si usas ImagenFormSet, el campo 'imagen' en cada formulario del formset
                # es para la subida de esas imágenes. No necesitas un campo 'gallery_images'
                # adicional en tu VentaForm principal.
                # Si 'gallery_images' es un campo custom en tu plantilla no manejado por el formset,
                # entonces esta lógica podría ser necesaria, pero es más común que el formset maneje
                # todas las imágenes asociadas.
                # Si quieres que los usuarios puedan subir más imágenes además de las que vienen
                # del formset (por ejemplo, con un botón "agregar más imágenes"), entonces
                # tendrías que asegurarte de que esas imágenes se manejen a través de formularios
                # adicionales o que el formset sea dinámico.
                # Por ahora, asumo que el formset es la forma principal de agregar/editar imágenes.
                # Si 'gallery_images' es un input name separado, y quieres que funcione así:
                # for uploaded_file in request.FILES.getlist('gallery_images'):
                #     Imagen.objects.create(
                #         content_object=venta,
                #         imagen=uploaded_file,
                #         descripcion=""
                #     )
                # Esto es válido, pero significa que no estás usando el ImagenForm para esas subidas.
                # Es mejor usar el formset para todo para tener validación y consistencia.
                # Por lo tanto, he comentado tu "NUEVA LÓGICA" a menos que tengas un caso de uso específico.

            messages.success(request, 'Propiedad de venta y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la propiedad de venta. Por favor, revisa los datos.')
    else:
        venta_form = VentaForm(instance=venta)
        # Cuando editas, el formset necesita la instancia para precargar las imágenes existentes
        formset = ImagenFormSet(instance=venta)

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

    if arriendo.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para editar esta propiedad.')
        return redirect('detalle_arriendo', pk=pk)

    if request.method == 'POST':
        arriendo_form = ArriendoForm(request.POST, request.FILES, instance=arriendo)
        formset = ImagenFormSet(request.POST, request.FILES, instance=arriendo)
        if arriendo_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                arriendo_form.save()
                formset.save() # Guarda y actualiza las instancias de Imagen

                # Comentado por las mismas razones que en editar_venta
                # if request.FILES.getlist('gallery_images'):
                #    for uploaded_file in request.FILES.getlist('gallery_images'):
                #        Imagen.objects.create(
                #            content_object=arriendo,
                #            imagen=uploaded_file,
                #            descripcion=""
                #        )

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

@login_required
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if venta.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para eliminar esta propiedad.')
        return redirect('detalle_venta', pk=pk)

    if request.method == 'POST':
        venta.delete()
        messages.success(request, 'La propiedad de venta ha sido eliminada exitosamente.')
        return redirect('perfil')

    return render(request, 'propiedades/confirmar_eliminar.html', {'objeto': venta, 'tipo': 'venta'})

@login_required
def eliminar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)

    if arriendo.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para eliminar esta propiedad.')
        return redirect('detalle_arriendo', pk=pk)

    if request.method == 'POST':
        arriendo.delete()
        messages.success(request, 'La propiedad de arriendo ha sido eliminada exitosamente.')
        return redirect('perfil')

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
    avatar, created = Avatar.objects.get_or_create(user=request.user)
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

    if request.method == 'POST':
        # Asegúrate de que el objeto Avatar exista para el usuario antes de intentar instanciar el formset
        # Si no existe, lo crea con la imagen por defecto.
        avatar_instance, created = Avatar.objects.get_or_create(user=request.user)

        form = EditProfileForm(request.POST, instance=request.user)
        avatar_form = AvatarForm(request.POST, request.FILES, instance=avatar_instance) # Usa la instancia asegurada

        if form.is_valid() and avatar_form.is_valid():
            form.save()
            avatar = avatar_form.save(commit=False) # Guarda el avatar
            avatar.user = request.user # Asegura que el usuario esté asignado (aunque ya lo hace get_or_create)
            avatar.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # En GET, asegúrate de que el objeto Avatar exista
        # Si no existe, lo crea con la imagen por defecto.
        avatar_instance, created = Avatar.objects.get_or_create(user=request.user)

        form = EditProfileForm(instance=request.user)
        avatar_form = AvatarForm(instance=avatar_instance) # Usa la instancia asegurada

    return render(request, 'propiedades/editarPerfil.html', {'form': form, 'avatar_form': avatar_form})

def about(request):
    return render(request, 'propiedades/about.html')


def register_request(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            inmobiliario_group, created = Group.objects.get_or_create(name='Inmobiliario')
            user.groups.add(inmobiliario_group)
            Avatar.objects.create(user=user)
            login(request, user)
            messages.success(request, "Registro exitoso.")
            return redirect("home")
        messages.error(request, "Registro fallido. Información inválida.")
    form = UserRegisterForm()
    # CAMBIA ESTA LÍNEA:
    return render(request, "registration/register.html", {"form": form})