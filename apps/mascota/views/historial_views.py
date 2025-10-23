"""
Vistas para gestionar el historial médico de mascotas
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.db.models import Q

from apps.mascota.models import Mascota
from apps.mascota.models_historial import HistorialMedico, Vacuna, RegistroVacuna


class HistorialMedicoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar el historial médico de una mascota"""
    model = HistorialMedico
    template_name = 'mascota/historial/list.html'
    context_object_name = 'eventos'
    paginate_by = 20
    
    def test_func(self):
        """Solo el propietario o veterinarios/admins pueden ver"""
        mascota = get_object_or_404(Mascota, pk=self.kwargs['mascota_pk'])
        return (
            self.request.user == mascota.propietario or
            self.request.user.role in ['VET', 'ADMIN']
        )
    
    def get_queryset(self):
        self.mascota = get_object_or_404(Mascota, pk=self.kwargs['mascota_pk'])
        queryset = HistorialMedico.objects.filter(mascota=self.mascota)
        
        # Filtro por tipo de evento
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_evento=tipo)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mascota'] = self.mascota
        context['title'] = f'Historial Médico - {self.mascota.nombre}'
        
        # Estadísticas
        context['total_eventos'] = HistorialMedico.objects.filter(mascota=self.mascota).count()
        context['vacunas_aplicadas'] = RegistroVacuna.objects.filter(mascota=self.mascota).count()
        context['proximas_citas'] = HistorialMedico.objects.filter(
            mascota=self.mascota,
            fecha_proxima__isnull=False,
            estado='pendiente'
        ).count()
        
        # Breadcrumb
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mis Mascotas', 'url': reverse_lazy('mascota:main_register')},
            {'label': self.mascota.nombre, 'url': f'/mascota/{self.mascota.pk}/'},
            {'label': 'Historial Médico', 'url': None},
        ]
        
        return context


class HistorialMedicoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para crear un nuevo evento en el historial médico"""
    model = HistorialMedico
    template_name = 'mascota/historial/form.html'
    fields = [
        'tipo_evento', 'titulo', 'descripcion', 'fecha_evento',
        'fecha_proxima', 'estado', 'medicamentos', 'costo',
        'notas', 'archivo_adjunto', 'dias_anticipacion_recordatorio'
    ]
    
    def test_func(self):
        """Solo veterinarios/admins pueden crear registros"""
        return self.request.user.role in ['VET', 'ADMIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.mascota = get_object_or_404(Mascota, pk=self.kwargs['mascota_pk'])
        context['mascota'] = self.mascota
        context['title'] = f'Nuevo Evento - {self.mascota.nombre}'
        context['is_create'] = True
        return context
    
    def form_valid(self, form):
        self.mascota = get_object_or_404(Mascota, pk=self.kwargs['mascota_pk'])
        form.instance.mascota = self.mascota
        form.instance.veterinario = self.request.user
        
        messages.success(
            self.request,
            f'Evento "{form.instance.titulo}" registrado exitosamente'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('mascota:historial_list', kwargs={'mascota_pk': self.mascota.pk})


class RegistroVacunaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para registrar una vacuna aplicada"""
    model = RegistroVacuna
    template_name = 'mascota/historial/vacuna_form.html'
    fields = ['vacuna', 'fecha_aplicacion', 'fecha_proxima', 'lote', 'notas']
    
    def test_func(self):
        """Solo veterinarios/admins pueden registrar vacunas"""
        return self.request.user.role in ['VET', 'ADMIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.mascota = get_object_or_404(Mascota, pk=self.kwargs['mascota_pk'])
        context['mascota'] = self.mascota
        context['title'] = f'Registrar Vacuna - {self.mascota.nombre}'
        
        # Lista de vacunas aplicadas
        context['vacunas_aplicadas'] = RegistroVacuna.objects.filter(
            mascota=self.mascota
        ).order_by('-fecha_aplicacion')
        
        return context
    
    def form_valid(self, form):
        self.mascota = get_object_or_404(Mascota, pk=self.kwargs['mascota_pk'])
        form.instance.mascota = self.mascota
        form.instance.veterinario = self.request.user
        
        messages.success(
            self.request,
            f'Vacuna "{form.instance.vacuna.nombre}" registrada exitosamente'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('mascota:historial_list', kwargs={'mascota_pk': self.mascota.pk})


class CartillaVacunacionView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para mostrar la cartilla de vacunación completa"""
    model = Mascota
    template_name = 'mascota/historial/cartilla_vacunacion.html'
    context_object_name = 'mascota'
    pk_url_kwarg = 'mascota_pk'
    
    def test_func(self):
        """Solo el propietario o veterinarios/admins pueden ver"""
        mascota = self.get_object()
        return (
            self.request.user == mascota.propietario or
            self.request.user.role in ['VET', 'ADMIN']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota = self.get_object()
        
        context['title'] = f'Cartilla de Vacunación - {mascota.nombre}'
        context['vacunas_aplicadas'] = RegistroVacuna.objects.filter(
            mascota=mascota
        ).order_by('-fecha_aplicacion')
        
        # Vacunas pendientes (próximas a vencer)
        from django.utils import timezone
        from datetime import timedelta
        
        context['vacunas_proximas'] = RegistroVacuna.objects.filter(
            mascota=mascota,
            fecha_proxima__isnull=False,
            fecha_proxima__gte=timezone.now().date(),
            fecha_proxima__lte=timezone.now().date() + timedelta(days=30)
        ).order_by('fecha_proxima')
        
        # Breadcrumb
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mis Mascotas', 'url': reverse_lazy('mascota:main_register')},
            {'label': mascota.nombre, 'url': f'/mascota/{mascota.pk}/'},
            {'label': 'Cartilla de Vacunación', 'url': None},
        ]
        
        return context
