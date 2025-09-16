from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from apps.autenticacion.models import User
from apps.autenticacion.utils.validar_cedula import valida_cedula

class BaseUserForm(forms.ModelForm):
    """Formulario base para usuarios con campos comunes"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'dni', 
                  'phone', 'direction', 'image', 'role']
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Nombre de usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Correo electrónico'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Apellido'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Cédula'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Teléfono'
            }),
            'direction': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Dirección'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'accept': 'image/*'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            })
        }
    
    def clean_dni(self):
        """Valida la cédula ecuatoriana"""
        dni = self.cleaned_data.get('dni')
        if dni:
            try:
                valida_cedula(dni)
            except forms.ValidationError as e:
                self.add_error('dni', e)
        return dni

    def clean_username(self):
        """Asegura que el nombre de usuario sea único"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()  # Convertir a minúsculas
        return username


class UserCreateForm(UserCreationForm, BaseUserForm):
    """Formulario para crear nuevos usuarios con contraseña"""
    
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña', 
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta(BaseUserForm.Meta):
        pass

    def clean_password2(self):
        """Verifica que las contraseñas coincidan"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2


class UserEditForm(BaseUserForm):
    """Formulario para editar usuarios existentes"""
    
    class Meta(BaseUserForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo username sea de solo lectura si ya existe el usuario
        if self.instance and self.instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['username'].help_text = 'El nombre de usuario no puede ser modificado'


class AdminUserCreateForm(UserCreateForm):
    """Formulario para que los administradores creen usuarios con campos adicionales"""
    
    # Campos específicos para veterinario
    specialization = forms.CharField(
        label='Especialización',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Especialización del veterinario'
        })
    )
    
    license_number = forms.CharField(
        label='Número de licencia',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Número de licencia profesional'
        })
    )
    
    class Meta(UserCreateForm.Meta):
        fields = UserCreateForm.Meta.fields + ['is_active', 'is_staff', 'is_superuser']
        
        widgets = {
            **UserCreateForm.Meta.widgets,
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded text-primary-600 border-neutral-300 focus:ring-primary-500'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'rounded text-primary-600 border-neutral-300 focus:ring-primary-500'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'rounded text-primary-600 border-neutral-300 focus:ring-primary-500'
            })
        }


class AdminUserEditForm(UserEditForm):
    """Formulario para que los administradores editen usuarios con campos adicionales"""
    
    # Campos específicos para veterinario
    specialization = forms.CharField(
        label='Especialización',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Especialización del veterinario'
        })
    )
    
    license_number = forms.CharField(
        label='Número de licencia',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Número de licencia profesional'
        })
    )
    
    class Meta(UserEditForm.Meta):
        fields = UserEditForm.Meta.fields + ['is_active', 'is_staff', 'is_superuser']
        
        widgets = {
            **UserEditForm.Meta.widgets,
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded text-primary-600 border-neutral-300 focus:ring-primary-500'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'rounded text-primary-600 border-neutral-300 focus:ring-primary-500'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'rounded text-primary-600 border-neutral-300 focus:ring-primary-500'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el usuario es veterinario, cargar los valores de los campos específicos
        if self.instance and hasattr(self.instance, 'role') and self.instance.role == User.Role.VET:
            if hasattr(self.instance, 'specialization'):
                self.fields['specialization'].initial = self.instance.specialization
            if hasattr(self.instance, 'license_number'):
                self.fields['license_number'].initial = self.instance.license_number


class VeterinarianUserForm(BaseUserForm):
    """Formulario específico para usuarios veterinarios con campos adicionales"""
    
    class Meta(BaseUserForm.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'dni', 
                  'phone', 'direction', 'image', 'specialization', 'license_number']
        
        widgets = {
            **BaseUserForm.Meta.widgets,
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Especialización'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Número de licencia'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el rol como veterinario por defecto
        self.fields['role'].initial = User.Role.VET
        self.fields['role'].widget = forms.HiddenInput()


class VeterinarianCreateForm(UserCreateForm, VeterinarianUserForm):
    """Formulario para crear usuarios veterinarios"""
    
    class Meta(VeterinarianUserForm.Meta):
        pass


class VeterinarianEditForm(UserEditForm, VeterinarianUserForm):
    """Formulario para editar usuarios veterinarios"""
    
    class Meta(VeterinarianUserForm.Meta):
        pass


class OwnerUserForm(BaseUserForm):
    """Formulario específico para dueños de mascotas"""
    
    class Meta(BaseUserForm.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'dni', 
                  'phone', 'direction', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el rol como dueño por defecto
        self.fields['role'].initial = User.Role.OWNER
        self.fields['role'].widget = forms.HiddenInput()


class OwnerCreateForm(UserCreateForm, OwnerUserForm):
    """Formulario para crear usuarios dueños"""
    
    class Meta(OwnerUserForm.Meta):
        pass


class OwnerEditForm(UserEditForm, OwnerUserForm):
    """Formulario para editar usuarios dueños"""
    
    class Meta(OwnerUserForm.Meta):
        pass


class UserPasswordChangeForm(forms.Form):
    """Formulario para cambiar la contraseña de un usuario"""
    
    old_password = forms.CharField(
        label='Contraseña actual', 
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Contraseña actual'
        })
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña', 
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Nueva contraseña'
        })
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña', 
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )

    def clean_new_password2(self):
        """Verifica que las nuevas contraseñas coincidan"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

class RegisterForm(UserCreateForm, BaseUserForm):
    class Meta(BaseUserForm.Meta):
        fields = [
            'username', 'email', 'first_name', 'last_name', 'dni',
            'phone', 'direction', 'image', 'password1', 'password2', 'role'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = User.Role.OWNER
        self.fields['role'].widget = forms.HiddenInput()