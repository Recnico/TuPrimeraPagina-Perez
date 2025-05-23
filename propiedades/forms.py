from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from .models import Corredor, Venta, Arriendo , Imagen
from .models import Avatar
from django.contrib.contenttypes.forms import generic_inlineformset_factory 
from django.forms.widgets import ClearableFileInput

class CorredorForm(forms.ModelForm):
    class Meta:
        model = Corredor
        fields = '__all__'

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = '__all__'

class ArriendoForm(forms.ModelForm):
    class Meta:
        model = Arriendo
        fields = '__all__'

class BuscarPropiedadForm(forms.Form):
    direccion = forms.CharField(label="Dirección", max_length=200, required=False)

class VentaSearchForm(forms.Form):
    direccion = forms.CharField(required=False, label='Buscar por dirección')
    precio_min = forms.IntegerField(required=False, label='Precio mínimo')
    precio_max = forms.IntegerField(required=False, label='Precio máximo')
    corredor = forms.ModelChoiceField(queryset=Corredor.objects.all(), required=False, label='Corredor')

class EditProfileForm(UserChangeForm): # Usar un nombre descriptivo como EditProfileForm
    class Meta:
        model = get_user_model() 
        fields = ('username', 'email', 'first_name', 'last_name') 

        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = ['imagen']

class ImagenForm(forms.ModelForm):
    imagen = forms.ImageField(widget=ClearableFileInput) # 
    class Meta:
        model = Imagen
        fields = ['imagen', 'descripcion', 'orden'] 


ImagenFormSet = generic_inlineformset_factory(
    Imagen,         # ¡Aquí el modelo hijo es el primer argumento!
    form=ImagenForm,
    extra=3,
    can_delete=True,
    fields=['imagen', 'descripcion', 'orden']
)