from django.views.generic import UpdateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from apps.autenticacion.models import User, UserFaceEmbedding
from apps.autenticacion.forms.users_form import (
    VeterinarianEditForm, OwnerEditForm
)
from apps.autenticacion.forms.profile_form import ProfilePasswordChangeForm


class ProfileView(LoginRequiredMixin, DetailView):
    """Vista para ver el perfil del usuario actual"""
    model = User
    template_name = 'autenticacion/profile/detail.html'
    context_object_name = 'user_profile'
    
    def get_object(self, queryset=None):
        return self.request.user
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mi Perfil'
        
        # Obtener información de biometría facial
        try:
            face_embedding = UserFaceEmbedding.objects.get(
                user=self.request.user,
                is_active=True
            )
            context['has_biometry'] = True
            context['biometry_active'] = face_embedding.allow_login
            context['biometry_stats'] = {
                'successful_logins': face_embedding.successful_logins,
                'failed_attempts': face_embedding.failed_attempts,
                'registered_at': face_embedding.created_at,
                'last_login': face_embedding.last_successful_login
            }
        except UserFaceEmbedding.DoesNotExist:
            context['has_biometry'] = False
            context['biometry_active'] = False
            context['biometry_stats'] = None
        
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mi perfil'}
        ]
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para que el usuario actualice su propio perfil"""
    model = User
    template_name = 'autenticacion/profile/form.html'
    success_url = reverse_lazy('auth:profile')
    
    def get_form_class(self):
        """Seleccionar el formulario adecuado según el rol del usuario"""
        user = self.request.user
        
        if user.is_vet:
            return VeterinarianEditForm
        else:  # Por defecto se usa el formulario para dueños
            return OwnerEditForm
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Actualizar Perfil'
        context['submit_text'] = 'Guardar Cambios'
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mi perfil', 'url': reverse_lazy('auth:profile')},
            {'label': 'Actualizar Perfil'}
        ]
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)
        
        
@method_decorator(login_required, name='dispatch')
class ProfilePasswordChangeView(FormView):
    """Vista para que el usuario cambie su contraseña"""
    form_class = ProfilePasswordChangeForm
    template_name = 'autenticacion/profile/password_change.html'
    success_url = reverse_lazy('auth:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cambiar Contraseña'
        context['submit_text'] = 'Cambiar Contraseña'
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mi perfil', 'url': reverse_lazy('auth:profile')},
            {'label': 'Cambio de contraseña'}
        ]
        return context
    
    def form_valid(self, form):
        user = form.save()
        # Actualizar la sesión para que el usuario no sea desconectado
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Tu contraseña ha sido actualizada correctamente.')
        return super().form_valid(form)
