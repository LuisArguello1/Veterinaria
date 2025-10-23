from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from apps.mascota.models import Mascota
from django import forms


class MascotaUpdateForm(forms.ModelForm):
    """Formulario para editar datos de la mascota"""
    
    class Meta:
        model = Mascota
        fields = [
            'nombre', 'raza', 'sexo', 'fecha_nacimiento', 
            'edad', 'edad_unidad', 'peso', 'color',
            'estado_corporal', 'etapa_vida', 
            'caracteristicas_especiales', 'foto_perfil'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'placeholder': 'Nombre de la mascota'
            }),
            'raza': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'placeholder': 'Ej: Labrador, Bulldog'
            }),
            'sexo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'type': 'date'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'placeholder': 'Edad',
                'min': '0'
            }),
            'edad_unidad': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'placeholder': 'Peso en kg',
                'step': '0.01',
                'min': '0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'placeholder': 'Ej: Café, Negro, Blanco'
            }),
            'estado_corporal': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all'
            }),
            'etapa_vida': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all'
            }),
            'caracteristicas_especiales': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all',
                'placeholder': 'Características especiales, marcas, comportamiento, etc.',
                'rows': 4
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'foto-perfil-input'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'raza': 'Raza',
            'sexo': 'Sexo',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'edad': 'Edad',
            'edad_unidad': 'Unidad',
            'peso': 'Peso (kg)',
            'color': 'Color',
            'estado_corporal': 'Estado Corporal',
            'etapa_vida': 'Etapa de Vida',
            'caracteristicas_especiales': 'Características Especiales',
            'foto_perfil': 'Foto de Perfil'
        }


class MascotaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar una mascota"""
    model = Mascota
    form_class = MascotaUpdateForm
    template_name = 'mascota/edit_mascota.html'
    context_object_name = 'mascota'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Mascota - {self.object.nombre}'
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': '/'},
            {'label': 'Mis Mascotas', 'url': reverse_lazy('mascota:main_register')},
            {'label': self.object.nombre, 'url': self.object.get_absolute_url()},
            {'label': 'Editar', 'url': None},
        ]
        return context
    
    def test_func(self):
        """Verificar que el usuario sea el propietario o admin"""
        mascota = self.get_object()
        return (
            self.request.user == mascota.propietario or 
            self.request.user.role == 'ADMIN'
        )
    
    def get_success_url(self):
        """Redirigir al detalle de la mascota después de editar"""
        return reverse_lazy('mascota:detalle', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Procesar formulario válido"""
        messages.success(
            self.request, 
            f'✓ Información de {form.instance.nombre} actualizada correctamente'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Procesar formulario inválido"""
        messages.error(
            self.request,
            'Error al actualizar la información. Por favor revisa los campos.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional"""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar {self.object.nombre}'
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mis Mascotas', 'url': reverse_lazy('mascota:main_register')},
            {'label': self.object.nombre, 'url': reverse_lazy('mascota:detalle', kwargs={'pk': self.object.pk})},
            {'label': 'Editar'}
        ]
        return context
