from django.shortcuts import render, redirect
from .forms import CorredorForm, ArriendoForm, VentaForm, VentaSearchForm
from .models import Venta

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