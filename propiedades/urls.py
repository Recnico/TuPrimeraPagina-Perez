from django.urls import path , include
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('agregar_corredor/', views.agregar_corredor, name='agregar_corredor'),
    path('agregar_arriendo/', views.agregar_arriendo, name='agregar_arriendo'),
    path('agregar_venta/', views.agregar_venta, name='agregar_venta'),
    path('buscar_venta/', views.buscar_venta, name='buscar_venta'),
    path('perfil/', views.perfil, name='perfil'),
    path('editarPerfil/', views.editarPerfil, name='editar_perfil'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('cambiar-clave/', auth_views.PasswordChangeView.as_view(template_name='propiedades/cambio_contrasenia.html',success_url=reverse_lazy('cambio_contrasenia_exitoso')), name='cambiar_contrasenia'), 
    path('cambiar-clave/exito/',auth_views.PasswordChangeDoneView.as_view(template_name='propiedades/cambio_contrasenia_exitoso.html'),name='cambio_contrasenia_exitoso'),
    path('cerrar_sesion/', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name='cerrar_sesion'),

]