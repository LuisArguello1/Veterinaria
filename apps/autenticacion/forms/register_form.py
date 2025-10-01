from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.autenticacion.models import User

class RegisterForm(UserCreationForm):
    """Formulario especializado para el registro de dueños de mascotas"""
    
    # Hacer dni obligatorio
    dni = forms.CharField(
        max_length=10, 
        required=True, 
        error_messages={'required': 'La cédula es obligatoria'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'dni',
            'phone', 'direction', 'image', 'password1', 'password2', 'role'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el rol como OWNER por defecto
        self.fields['role'].initial = User.Role.OWNER
        self.fields['role'].widget = forms.HiddenInput()
        
        # Actualizar los widgets para tener iconos
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'correo@ejemplo.com'
        })
        self.fields['first_name'].widget = forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tu nombre'
        })
        self.fields['last_name'].widget = forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tu apellido'
        })
        self.fields['dni'].widget = forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Número de cédula',
            'required': True,
        })
        self.fields['phone'].widget = forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Número telefónico'
        })
        self.fields['direction'].widget = forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tu dirección completa'
        })
        self.fields['image'].widget = forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'accept': 'image/*'
        })
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': '••••••••'
        })
        
    def clean_username(self):
        """Asegura que el nombre de usuario sea único y en minúsculas"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()  # Convertir a minúsculas
        return username
        
    def clean_dni(self):
        """Valida la cédula ecuatoriana"""
        dni = self.cleaned_data.get('dni')
        if not dni:
            raise forms.ValidationError("Debe ingresar su número de cédula")
            
        # Validar el formato de cédula
        from apps.autenticacion.utils.validar_cedula import valida_cedula
        try:
            valida_cedula(dni)
        except forms.ValidationError as e:
            self.add_error('dni', e)
            
        # Verificar si la cédula ya está registrada
        User = self.Meta.model
        if User.objects.filter(dni=dni).exists() and (self.instance.pk is None or self.instance.dni != dni):
            raise forms.ValidationError("Esta cédula ya está registrada en el sistema")
            
        return dni