from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from apps.autenticacion.models import User

class ProfilePasswordChangeForm(PasswordChangeForm):
    """Formulario personalizado para cambiar la contraseña del propio usuario"""
    
    old_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Ingrese su contraseña actual'
        })
    )
    
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Ingrese su nueva contraseña'
        })
    )
    
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirme su nueva contraseña'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el formulario tiene ayuda para el campo de nueva contraseña, convertirla a lista
        if self.fields['new_password1'].help_text:
            self.fields['new_password1'].help_text = [
                line for line in self.fields['new_password1'].help_text.split('\n') if line.strip()
            ]