"""
URL configuration for miweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name='cerrar_sesion'),
    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='propiedades/cambio_contrasenia.html',success_url=reverse_lazy('cambio_contrasenia_exitoso')), name='cambiar_contrasenia'),
    path('accounts/password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='propiedades/cambio_contrasenia_exitoso.html'), name='cambio_contrasenia_exitoso'),

    path('', include('propiedades.urls')),
    
]
if settings.DEBUG: # hacemos esta validación para que servir los estaticos desde django solo en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)