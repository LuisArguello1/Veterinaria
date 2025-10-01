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
            return redirect('auth:Dashboard')  # usa el name real de tu dashboard
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Procesa el formulario válido y crea el usuario"""
        try:
            # Crear el objeto usuario pero no guardarlo todavía
            user = form.save(commit=False)
            
            # Asegurarse de que el rol sea siempre OWNER
            user.role = user.Role.OWNER
            
            # Verificar que se ha proporcionado la cédula
            if not user.dni:
                form.add_error('dni', 'El campo de cédula es obligatorio.')
                return self.form_invalid(form)
            
            # Configurar contraseña segura
            password = form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
            
            # Guardar el usuario
            user.save()
            
            # Iniciar sesión automáticamente especificando el backend
            from django.contrib.auth import authenticate
            from django.contrib.auth import get_user_model
            
            # Usar el backend de autenticación por defecto (ModelBackend)
            from django.contrib.auth.backends import ModelBackend
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Mensaje de éxito para la redirección
            messages.success(
                self.request, 
                f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.'
            )
            
            return super().form_valid(form)
            
        except Exception as e:
            # Capturar cualquier error y manejarlo adecuadamente
            if 'dni' in str(e).lower():
                form.add_error('dni', 'Por favor, proporcione un número de cédula válido.')
            else:
                form.add_error(None, f'Error al crear el usuario: {str(e)}')
            return self.form_invalid(form)
