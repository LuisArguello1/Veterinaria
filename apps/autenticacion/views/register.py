# views.py
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect

from apps.autenticacion.forms.register_form import RegisterForm


class RegisterView(FormView):
    """Vista para el registro de nuevos usuarios (dueños de mascotas)"""
    template_name = 'autenticacion/auth/register.html'
    form_class = RegisterForm
    # Si tu mensaje dice "Por favor inicia sesión", redirige al login:
    success_url = reverse_lazy('auth:login')

    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, no debe ver /register
        if request.user.is_authenticated:
            return redirect('dashboard')  # usa el name real de tu dashboard
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Procesa el formulario válido y crea el usuario"""
        user = form.save(commit=False)

        # Asegurarse de que el rol sea siempre OWNER
        user.role = user.Role.OWNER
        
        # Configurar contraseña segura
        password = form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        # Guardar el usuario
        user.save()
        
        # Iniciar sesión automáticamente
        login(self.request, user)
        
        # Mensaje de éxito para la redirección
        messages.success(
            self.request, 
            f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.'
        )
        
        return super().form_valid(form)
