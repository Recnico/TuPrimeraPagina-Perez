from django.urls import path , include
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('agregar_corredor/', views.agregar_corredor, name='agregar_corredor'),
    path('agregar_arriendo/', views.agregar_arriendo, name='agregar_arriendo'),
    path('agregar_venta/', views.agregar_o_editar_venta, name='agregar_venta'),
    path('venta/<int:pk>/', views.detalle_venta, name='detalle_venta'), 
    path('venta/editar/<int:pk>/', views.agregar_o_editar_venta, name='editar_venta'),
     path('venta/eliminar/<int:pk>/', views.eliminar_venta, name='eliminar_venta'),
    path('arriendo/<int:pk>/', views.detalle_arriendo, name='detalle_arriendo'),
    path('arriendo/editar/<int:pk>/', views.editar_arriendo, name='editar_arriendo'),
    path('arriendo/eliminar/<int:pk>/', views.eliminar_arriendo, name='eliminar_arriendo'),
    path('buscar_arriendo/', views.buscar_arriendo, name='buscar_arriendo'), 
    path('buscar_venta/', views.buscar_venta, name='buscar_venta'),
    path('perfil/', views.perfil, name='perfil'),
    path('editarPerfil/', views.editarPerfil, name='editar_perfil'),
    path('about/', views.about, name='about'),
    path('register/', views.register_request, name='register'),
    path('pages/', views.PostListView.as_view(), name='listado_posts'), # Listado de posts
    path('pages/crear/', views.PostCreateView.as_view(), name='crear_post'), # Crear nuevo post
    path('pages/<int:pk>/', views.PostDetailView.as_view(), name='detalle_post'), # Detalle de un post
    path('pages/<int:pk>/editar/', views.PostUpdateView.as_view(), name='editar_post'), # Editar post
    path('pages/<int:pk>/eliminar/', views.PostDeleteView.as_view(), name='eliminar_post'), # Eliminar post

]