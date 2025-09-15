from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from apps.autenticacion.models import User
from apps.autenticacion.forms.users_form import (
    VeterinarianEditForm, OwnerEditForm
)


class ProfileView(LoginRequiredMixin, DetailView):
    """Vista para ver el perfil del usuario actual"""
    model = User
    template_name = 'autenticacion/profile/detail.html'
    context_object_name = 'user_profile'
    
    def get_object(self, queryset=None):
        return self.request.user


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
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)
