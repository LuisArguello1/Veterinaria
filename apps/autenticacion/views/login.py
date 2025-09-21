from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.autenticacion.forms.login_form import LoginForm
from apps.autenticacion.models import User

class LoginView(FormView):
    """Vista para el inicio de sesión de usuarios"""
    template_name = 'autenticacion/auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('auth:Dashboard')

    def form_valid(self, form):
        """Procesa el formulario válido"""
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        # Autenticar usuario usando email
        user = authenticate(request=self.request, email=email, password=password)

        if user is not None:
            if user.is_active:
                login(self.request, user)
                messages.success(self.request, f'¡Bienvenido {user.get_full_name()}!')
                return super().form_valid(form)
            else:
                messages.error(self.request, 'Tu cuenta está desactivada.')
        else:
            messages.error(self.request, 'Correo o contraseña incorrectos.')

        return self.form_invalid(form)

class LogoutView(LoginRequiredMixin, RedirectView):
    """Vista para cerrar sesión"""
    url = reverse_lazy('auth:login')
    
    def get(self, request, *args, **kwargs):
        """Cierra la sesión del usuario y redirecciona"""
        logout(request)
        messages.success(request, '¡Has cerrado sesión exitosamente!')
        return super().get(request, *args, **kwargs)
