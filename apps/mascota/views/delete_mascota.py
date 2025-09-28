from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from apps.mascota.models import Mascota, ImagenMascota, EmbeddingStore


class MascotaDeleteView(LoginRequiredMixin, DeleteView):
    model = Mascota
    success_url = reverse_lazy('mascota:main_register')

    def get_queryset(self):
        return Mascota.objects.filter(propietario=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        mascota_nombre = self.object.nombre

        # Eliminar el objeto
        self.object.delete()

        # Si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'La mascota "{mascota_nombre}" fue eliminada.'
            }, status=200)

        # Si es una petición normal (no AJAX)
        messages.success(request, f'La mascota "{mascota_nombre}" y todos sus datos han sido eliminados.')
        return super().delete(request, *args, **kwargs)


class BiometriaDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar solo los datos biométricos de una mascota"""
    model = Mascota
    template_name = 'generic/delete_mixin.html'
    success_url = reverse_lazy('mascota:main_register')
    context_object_name = 'mascota'
    
    def get_queryset(self):
        """Solo permitir eliminar datos biométricos de mascotas del usuario autenticado"""
        return Mascota.objects.filter(propietario=self.request.user)
    
    def get_object(self, queryset=None):
        """Obtener la mascota y verificar permisos"""
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        return obj
    
    def post(self, request, *args, **kwargs):
        """Procesa la eliminación de los datos biométricos solamente"""
        self.object = self.get_object()
        
        # Obtener información antes de eliminar
        mascota_nombre = self.object.nombre
        
        # Eliminar solo imágenes biométricas y embeddings
        imagenes_biometricas = ImagenMascota.objects.filter(
            mascota=self.object, 
            is_biometrica=True
        )
        
        # Contar cuántas imágenes se van a eliminar
        count_imagenes = imagenes_biometricas.count()
        
        # Eliminar embeddings asociados (se eliminan automáticamente por CASCADE al eliminar imágenes)
        embeddings_count = EmbeddingStore.objects.filter(mascota=self.object).count()
        
        # Eliminar las imágenes biométricas
        imagenes_biometricas.delete()
        
        # Resetear el estado de biometría entrenada
        self.object.biometria_entrenada = False
        self.object.confianza_biometrica = None
        self.object.save()
        
        messages.success(
            request, 
            f'Datos biométricos de "{mascota_nombre}" eliminados: {count_imagenes} imágenes y {embeddings_count} embeddings.'
        )
        
        # Redirigir sin eliminar la mascota
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        """Redirigir a la pestaña de biometría de la mascota"""
        return f"{reverse_lazy('mascota:main_register')}?biometria_id={self.object.id}"