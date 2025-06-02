from django.shortcuts import render, redirect, get_object_or_404
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm, EditProfileForm, AvatarForm, ImagenFormSet, UserRegisterForm , BuscarPropiedadForm , ContactoPropiedadForm
from .models import Venta, Avatar, Imagen, Arriendo, Corredor , Post
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
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.core.mail import send_mail
from django.conf import settings


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
                arriendo.usuario = request.user 
                arriendo.save()
                imagenes = formset.save(commit=False)
                for imagen in imagenes:
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

def agregar_o_editar_venta(request, pk=None):
    venta_instance = None
    is_edit = False

    if pk: # Si se proporciona un PK, estamos en modo edición
        venta_instance = get_object_or_404(Venta, pk=pk)
        is_edit = True
    
    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta_instance)
        
        # Inicializa el formset SÓLO si estamos editando (para gestionar imágenes existentes)
        formset = None
        if is_edit:
            formset = ImagenFormSet(request.POST, request.FILES, instance=venta_instance)
        
        all_forms_valid = False

        if venta_form.is_valid():
            if is_edit: 
                if formset and formset.is_valid(): 
                    all_forms_valid = True
                elif not formset: 
                    messages.error(request, 'Error interno: el formset no pudo ser inicializado para edición.')
            else: 
                all_forms_valid = True
        
        if all_forms_valid:
            with transaction.atomic():
                venta = venta_form.save(commit=False)
                if not is_edit: 
                    venta.usuario = request.user
                venta.save()

                if is_edit and formset:
                    imagenes_formset = formset.save(commit=False)
                    for imagen in imagenes_formset:
                        imagen.content_object = venta
                        imagen.save()
                    for imagen_to_delete in formset.deleted_objects:
                        imagen_to_delete.delete()

                if 'gallery_images' in request.FILES:
                    for f in request.FILES.getlist('gallery_images'):
                        Imagen.objects.create(content_object=venta, imagen=f)

            messages.success(request, 'Propiedad y galería de imágenes guardadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk) 
        else:
            print("--- ERRORES DE VALIDACIÓN ---")
            if venta_form.errors:
                print("Errores en VentaForm:", venta_form.errors.as_json())
            if formset and formset.errors: 
                print("Errores generales en Formset:", formset.errors)
                for i, form in enumerate(formset):
                    if form.errors:
                        print(f"Errores en el formulario de imagen #{i}:", form.errors.as_json())
            print("--- FIN DE ERRORES ---")
            
            messages.error(request, 'Hubo errores al guardar la propiedad. Por favor, revisa los datos.')

    else: 
        venta_form = VentaForm(instance=venta_instance)
        formset = ImagenFormSet(instance=venta_instance) if is_edit else None

    context = {
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Editar Venta' if is_edit else 'Agregar Nueva Venta',
        'is_edit': is_edit, 
    }
    return render(request, 'propiedades/agregar_venta.html', context)


def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    imagenes = venta.get_gallery_images()
    contacto_form = ContactoPropiedadForm() 

    if request.method == 'POST':
        contacto_form = ContactoPropiedadForm(request.POST)
        if contacto_form.is_valid():
            nombre = contacto_form.cleaned_data['nombre']
            email_remitente = contacto_form.cleaned_data['email']
            telefono = contacto_form.cleaned_data['telefono']
            mensaje_usuario = contacto_form.cleaned_data['mensaje']
            asunto = f"Solicitud de información sobre propiedad: {venta.direccion} (ID: {venta.pk})"
            mensaje_correo = f"""
            Has recibido una nueva solicitud de información para la propiedad:
            Dirección: {venta.direccion}
            ID de Propiedad: {venta.pk}
            Precio: ${venta.precio:,}
            Datos del interesado:
            Nombre: {nombre}
            Correo: {email_remitente}
            Teléfono: {telefono if telefono else 'No proporcionado'}
            Mensaje del interesado:
            {mensaje_usuario}
            """
            try:
                send_mail(
                    asunto,
                    mensaje_correo,
                    settings.EMAIL_HOST_USER,
                    [settings.DEFAULT_TO_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Tu solicitud ha sido enviada exitosamente. Nos pondremos en contacto contigo pronto.')
                return redirect('detalle_venta', pk=venta.pk)
            except Exception as e:
                messages.error(request, f'Hubo un error al enviar tu solicitud. Por favor, inténtalo de nuevo más tarde. Error: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario de contacto.')

    context = {
        'venta': venta,
        'imagenes': imagenes,
        'contacto_form': contacto_form, 
    }
    return render(request, 'propiedades/detalle_venta.html', context)

@login_required
def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if venta.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'No tienes permiso para editar esta propiedad.')
        return redirect('detalle_venta', pk=pk)

    if request.method == 'POST':
        venta_form = VentaForm(request.POST, request.FILES, instance=venta)
        formset = ImagenFormSet(request.POST, request.FILES, instance=venta)
        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta_form.save()
                formset.save() 

            messages.success(request, 'Propiedad de venta y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_venta', pk=venta.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la propiedad de venta. Por favor, revisa los datos.')
    else:
        venta_form = VentaForm(instance=venta)
        formset = ImagenFormSet(instance=venta)

    return render(request, 'propiedades/agregar_venta.html', { 
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Editar Venta',
        'is_edit': True,
    })

def detalle_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    imagenes = arriendo.get_gallery_images()
    contacto_form = ContactoPropiedadForm() 

    if request.method == 'POST':
        contacto_form = ContactoPropiedadForm(request.POST)
        if contacto_form.is_valid():
            nombre = contacto_form.cleaned_data['nombre']
            email_remitente = contacto_form.cleaned_data['email']
            telefono = contacto_form.cleaned_data['telefono']
            mensaje_usuario = contacto_form.cleaned_data['mensaje']
            asunto = f"Solicitud de información sobre propiedad: {arriendo.direccion} (ID: {arriendo.pk})"
            mensaje_correo = f"""
            Has recibido una nueva solicitud de información para la propiedad:
            Dirección: {arriendo.direccion}
            ID de Propiedad: {arriendo.pk}
            Precio: ${arriendo.precio_mensual:,}

            Datos del interesado:
            Nombre: {nombre}
            Correo: {email_remitente}
            Teléfono: {telefono if telefono else 'No proporcionado'}

            Mensaje del interesado:
            {mensaje_usuario}
            """
            try:
                send_mail(
                    asunto,
                    mensaje_correo,
                    settings.EMAIL_HOST_USER, 
                    [settings.DEFAULT_TO_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Tu solicitud ha sido enviada exitosamente. Nos pondremos en contacto contigo pronto.')
                return redirect('detalle_arriendo', pk=arriendo.pk)
            except Exception as e:
                messages.error(request, f'Hubo un error al enviar tu solicitud. Por favor, inténtalo de nuevo más tarde. Error: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario de contacto.')

    context = {
        'arriendo': arriendo,
        'imagenes': imagenes,
        'contacto_form': contacto_form, 
    }
    return render(request, 'propiedades/detalle_arriendo.html', context) 

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
                formset.save()

            messages.success(request, 'Propiedad de arriendo y galería de imágenes actualizadas correctamente.')
            return redirect('detalle_arriendo', pk=arriendo.pk)
        else:
            messages.error(request, 'Hubo errores al actualizar la propiedad de arriendo. Por favor, revisa los datos.')
    else:
        arriendo_form = ArriendoForm(instance=arriendo)
        formset = ImagenFormSet(instance=arriendo)

    return render(request, 'propiedades/agregar_arriendo.html', { 
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
        avatar_instance, created = Avatar.objects.get_or_create(user=request.user)
        form = EditProfileForm(request.POST, instance=request.user)
        avatar_form = AvatarForm(request.POST, request.FILES, instance=avatar_instance) # Usa la instancia asegurada

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
        avatar_instance, created = Avatar.objects.get_or_create(user=request.user)

        form = EditProfileForm(instance=request.user)
        avatar_form = AvatarForm(instance=avatar_instance)
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
    return render(request, "registration/register.html", {"form": form})

class PostListView(ListView):
    model = Post
    template_name = 'propiedades/post_list.html' 
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context['posts']:
            context['no_posts_message'] = "No hay posts de blog aún. ¡Sé el primero en crear uno!"
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'propiedades/post_detail.html'
    context_object_name = 'post'

class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView): 
    model = Post
    template_name = 'propiedades/post_form.html'
    fields = ['titulo', 'subtitulo', 'contenido', 'imagen_principal']
    success_url = reverse_lazy('listado_posts')

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): 
    template_name = 'propiedades/post_form.html'
    fields = ['titulo', 'subtitulo', 'contenido', 'imagen_principal']
    success_url = reverse_lazy('listado_posts')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.autor or self.request.user.is_staff or self.request.user.is_superuser

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): 
    model = Post
    template_name = 'propiedades/post_confirm_delete.html'
    success_url = reverse_lazy('listado_posts')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.autor or self.request.user.is_staff or self.request.user.is_superuser