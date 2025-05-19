from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('agregar_corredor/', views.agregar_corredor, name='agregar_corredor'),
    path('agregar_arriendo/', views.agregar_arriendo, name='agregar_arriendo'),
    path('agregar_venta/', views.agregar_venta, name='agregar_venta'),
    path('buscar_venta/', views.buscar_venta, name='buscar_venta'),
]