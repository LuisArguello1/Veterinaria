from django import forms

class LoginForm(forms.Form):
    """Formulario para el inicio de sesión de usuarios"""
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white text-gray-900',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white text-gray-900',
            'placeholder': '••••••••'
        })
    )

    def clean(self):
        """Validación personalizada del formulario"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email and not password:
            raise forms.ValidationError('Por favor ingrese su correo y contraseña')