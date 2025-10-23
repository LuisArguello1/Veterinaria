from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from apps.mascota.models import Mascota
from apps.mascota.forms import MascotaCreateForm
from apps.autenticacion.models_notification import Notification
import uuid


class MascotaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Vista para el registro de nuevas mascotas.
    
    Restricciones de acceso:
    - Solo usuarios con rol OWNER pueden registrar sus propias mascotas
    - Usuarios con rol ADMIN pueden registrar mascotas (asignándose como propietario)
    - Usuarios con rol VET NO pueden registrar mascotas
    """
    model = Mascota
    form_class = MascotaCreateForm
    template_name = 'mascota_registro/form.html'
    success_url = reverse_lazy('mascota:main_register')
    
    def test_func(self):
        """
        Verificar que el usuario tenga permiso para registrar mascotas.
        Solo OWNER y ADMIN pueden registrar mascotas.
        """
        user = self.request.user
        # Permitir acceso a OWNER y ADMIN, denegar a VET
        return user.role in ['OWNER', 'ADMIN']
    
    def handle_no_permission(self):
        """Manejar acceso denegado con mensaje personalizado"""
        messages.error(
            self.request,
            'No tiene permisos para registrar mascotas. '
            'Solo los propietarios y administradores pueden realizar esta acción.'
        )
        return redirect('mascota:main_register')
    
    def form_valid(self, form):
        """
        Procesar el formulario válido:
        1. Asignar el propietario (usuario actual)
        2. Generar UUID único para el QR
        3. Crear notificación de bienvenida
        4. Guardar la mascota
        """
        # Asignar el usuario actual como propietario
        form.instance.propietario = self.request.user
        
        # Generar UUID único para el QR code
        form.instance.uuid = uuid.uuid4()
        
        # Guardar la mascota
        response = super().form_valid(form)
        
        # Crear notificación de bienvenida para el propietario
        try:
            Notification.objects.create(
                user=self.request.user,
                tipo='SUCCESS',
                titulo=f'¡Bienvenido {form.instance.nombre}!',
                mensaje=f'La mascota {form.instance.nombre} ha sido registrada exitosamente en el sistema. '
                        f'Ahora puedes agregar datos biométricos, historial médico y más información.',
                metadata={
                    'mascota_id': form.instance.id,
                    'mascota_nombre': form.instance.nombre,
                    'action': 'mascota_registrada'
                }
            )
        except Exception as e:
            # No fallar si la notificación falla, solo registrar el error
            print(f"Error al crear notificación de registro: {e}")
        
        # Mensaje de éxito
        messages.success(
            self.request,
            f'¡Mascota "{form.instance.nombre}" registrada exitosamente! '
            f'Ahora puedes agregar imágenes biométricas y más información.'
        )
        
        return response
    
    def form_invalid(self, form):
        """Manejar formulario inválido con mensaje de error"""
        messages.error(
            self.request,
            'Hubo un error al registrar la mascota. Por favor, revise los campos e intente nuevamente.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional al template"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Registrar Nueva Mascota'
        context['user_role'] = self.request.user.role
        context['total_mascotas'] = Mascota.objects.filter(
            propietario=self.request.user
        ).count()
        return context
