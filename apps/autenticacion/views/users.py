from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.autenticacion.models import User
from apps.autenticacion.forms.users_form import (
    AdminUserCreateForm, AdminUserEditForm, UserPasswordChangeForm
)


class UserListView(LoginRequiredMixin, ListView):
    """Vista para listar usuarios con filtrado por roles y búsqueda"""
    model = User
    template_name = 'autenticacion/users/list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtra usuarios según parámetros de búsqueda y rol"""
        queryset = super().get_queryset()
        
        # Filtrado por términos de búsqueda
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(dni__icontains=search_query)
            )
        
        # Filtrado por rol
        role_filter = self.request.GET.get('role', '')
        if role_filter in [choice[0] for choice in User.Role.choices]:
            queryset = queryset.filter(role=role_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Agrega contexto adicional para la plantilla"""
        context = super().get_context_data(**kwargs)
        
        # Parámetros de filtrado
        context['search_query'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['role_choices'] = User.Role.choices
        context['user_now'] = self.request.user
        
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Gestión de Usuarios'}
        ]

        #Estadisticas
        context['Total_users'] = User.objects.filter().count()
        context['admin_users'] = User.objects.filter(role='ADMIN').count()
        context['veterinario_users'] = User.objects.filter(role='VET').count()
        context['dueno_users'] = User.objects.filter(role='OWNER').count()
        
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de un usuario específico"""
    model = User
    template_name = 'autenticacion/users/detail.html'
    context_object_name = 'user_obj'  # Evita conflicto con request.user
    
    def get_context_data(self, **kwargs):
        """Agrega breadcrumbs al contexto"""
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Gestión de Usuarios', 'url': reverse_lazy('auth:users_list')},
            {'label': f'Usuario: {user.username}'}
        ]
        
        return context

class UserCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear usuarios de cualquier rol"""
    model = User
    template_name = 'autenticacion/users/form.html'
    form_class = AdminUserCreateForm
    success_url = reverse_lazy('auth:users_list')
    
    def get_context_data(self, **kwargs):
        """Agrega título y breadcrumbs al contexto"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Usuario'
        context['submit_text'] = 'Crear Usuario'
        
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Gestión de Usuarios', 'url': reverse_lazy('auth:users_list')},
            {'label': 'Crear Usuario'}
        ]
        
        return context
    
    def form_valid(self, form):
        """Procesa el formulario válido y maneja campos específicos de rol"""
        user = form.save(commit=False)
        role = form.cleaned_data.get('role')
        
        # Procesa campos específicos para veterinarios
        if role == User.Role.VET:
            specialization = self.request.POST.get('specialization')
            license_number = self.request.POST.get('license_number')
            
            if specialization:
                user.specialization = specialization
            if license_number:
                user.license_number = license_number
        
        user.save()
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Maneja formularios inválidos"""
        messages.error(self.request, 'Error al crear el usuario.')
        return super().form_invalid(form)

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar usuarios existentes"""
    model = User
    template_name = 'autenticacion/users/form.html'
    form_class = AdminUserEditForm
    success_url = reverse_lazy('auth:users_list')
    
    def get_context_data(self, **kwargs):
        """Agrega título y breadcrumbs al contexto"""
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['title'] = 'Editar Usuario'
        context['submit_text'] = 'Actualizar Usuario'
        
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Gestión de Usuarios', 'url': reverse_lazy('auth:users_list')},
            {'label': f'Editar: {user.username}'}
        ]
        
        return context
    
    def form_valid(self, form):
        """Procesa el formulario válido y maneja campos específicos de rol"""
        user = form.save(commit=False)
        role = form.cleaned_data.get('role')
        
        # Procesa campos específicos para veterinarios
        if role == User.Role.VET:
            specialization = self.request.POST.get('specialization')
            license_number = self.request.POST.get('license_number')
            
            if specialization:
                user.specialization = specialization
            if license_number:
                user.license_number = license_number
        else:
            # Limpia campos específicos si no es veterinario
            if hasattr(user, 'specialization'):
                user.specialization = None
            if hasattr(user, 'license_number'):
                user.license_number = None
        
        user.save()
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Maneja formularios inválidos"""
        messages.error(self.request, 'Error al actualizar el usuario.')
        return super().form_invalid(form)

class UserDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar usuarios del sistema"""
    model = User
    template_name = 'generic/delete_mixin.html'
    success_url = reverse_lazy('auth:users_list')
    context_object_name = 'user_obj' 
    
    def post(self, request, *args, **kwargs):
        """Procesa la eliminación del usuario"""
        messages.success(self.request, 'Usuario eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class ChangePasswordView(LoginRequiredMixin, FormView):
    """Vista para cambiar la contraseña de un usuario específico"""
    template_name = 'autenticacion/users/change_password.html'
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('auth:users_list')
    
    def get_user(self):
        """Retorna el usuario seleccionado o el usuario actual"""
        if 'pk' in self.kwargs:
            return get_object_or_404(User, pk=self.kwargs['pk'])
        return self.request.user
    
    def get_context_data(self, **kwargs):
        """Agrega título y breadcrumbs al contexto"""
        context = super().get_context_data(**kwargs)
        
        user = self.get_user()
        context['user'] = user
        username = user.username
        context['title'] = f'Cambiar Contraseña: {username}'
        context['submit_text'] = 'Cambiar Contraseña'

        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Usuarios', 'url': reverse_lazy('auth:users_list')},
            {'label': f'Cambiar Contraseña: {username}'}
        ]
        
        return context
    
    def form_valid(self, form):
        """Verifica y actualiza la contraseña del usuario"""
        user = self.get_user()
        old_password = form.cleaned_data.get('old_password')
        new_password = form.cleaned_data.get('new_password1')
        
        user_actual = self.request.user

        # Verificar si el usuario que hace la solicitud es administrador (no necesita verificar contraseña antigua)
        is_admin_changing = user_actual.is_admin and user_actual.pk != user.pk
        
        # Verifica la contraseña actual (solo si no es un admin cambiando la contraseña de otro)
        if not is_admin_changing and not check_password(old_password, user.password):
            form.add_error('old_password', 'La contraseña actual es incorrecta.')
            return self.form_invalid(form)
        
        # Actualiza la contraseña
        user.password = make_password(new_password)
        user.save()
        
        messages.success(self.request, f'Contraseña de {user.username} actualizada exitosamente.')
        return redirect(self.success_url)
