from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from apps.autenticacion.models import User


class PasswordRecoveryRequestForm(PasswordResetForm):
    """Formulario para solicitar recuperación de contraseña"""
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white text-gray-900',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email'
        })
    )

    def clean_email(self):
        """Valida que el email exista en el sistema"""
        email = self.cleaned_data.get('email')
        
        if not User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(
                'No existe una cuenta activa asociada a este correo electrónico.'
            )
        
        return email


class PasswordRecoveryConfirmForm(SetPasswordForm):
    """Formulario para establecer nueva contraseña"""
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white text-gray-900',
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        }),
        help_text='Tu contraseña debe tener al menos 8 caracteres y no puede ser completamente numérica.'
    )
    
    new_password2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white text-gray-900',
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        }),
    )

    def clean_new_password2(self):
        """Valida que ambas contraseñas coincidan"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return password2
