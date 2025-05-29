from django import forms
from django.contrib.auth.forms import UserChangeForm ,UserCreationForm
from django.contrib.auth import get_user_model
from .models import Corredor, Venta, Arriendo , Imagen , Avatar
from django.contrib.contenttypes.forms import generic_inlineformset_factory 
from django.forms.widgets import ClearableFileInput

class CorredorForm(forms.ModelForm):
    class Meta:
        model = Corredor
        fields = '__all__'

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['direccion', 'precio', 'imagen_principal', 'Corredor', 'destacada']

class ArriendoForm(forms.ModelForm):
    class Meta:
        model = Arriendo
        fields = ['direccion', 'precio_mensual', 'imagen_principal', 'Corredor', 'destacada']

class BuscarPropiedadForm(forms.Form):
    direccion = forms.CharField(label="Dirección", max_length=200, required=False)

class VentaSearchForm(forms.Form):
    direccion = forms.CharField(required=False, label='Buscar por dirección')
    precio_min = forms.IntegerField(required=False, label='Precio mínimo')
    precio_max = forms.IntegerField(required=False, label='Precio máximo')
    corredor = forms.ModelChoiceField(queryset=Corredor.objects.all(), required=False, label='Corredor')

class EditProfileForm(UserChangeForm):
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
        # Aquí SOLO debes añadir la clase 'form-control'.
        # La clase 'is-invalid' se gestionará en la plantilla.
        for field_name, field in self.fields.items():
            if field_name != 'password':
                # Evita aplicar form-control a PasswordChangeForm si es un campo generado por UserChangeForm
                # aunque en este caso 'password' no es un campo directo editable
                field.widget.attrs['class'] = 'form-control'


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = ['imagen']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir la clase 'form-control' al campo de imagen
        self.fields['imagen'].widget.attrs['class'] = 'form-control'
        if self.fields['imagen'].errors:
             self.fields['imagen'].widget.attrs['class'] += ' is-invalid'



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
# NEW: User Registration Form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo Electrónico')

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',) # Add email, first_name, last_name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make first_name and last_name required (optional, but common for profiles)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        # Add labels for consistency
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'

    # Optional: Add clean methods for custom validation if needed
    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
