# apps/mascota/forms/simple_registro_form.py
from django import forms
from apps.mascota.models import Mascota


class SimpleMascotaRegistroForm(forms.ModelForm):
    """Formulario simplificado para registro de mascotas con predicción de IA integrada"""
    
    class Meta:
        model = Mascota
        fields = [
            'nombre', 'raza', 'etapa_vida', 'edad', 'edad_unidad',
            'sexo', 'fecha_nacimiento', 'peso', 'color',
            'caracteristicas_especiales', 'foto_perfil', 'estado_corporal'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Nombre de la mascota',
                'required': True
            }),
            'raza': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Raza (se puede predecir automáticamente)',
                'id': 'id_raza'
            }),
            'etapa_vida': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'id': 'id_etapa_vida'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Edad',
                'min': '0'
            }),
            'edad_unidad': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'sexo': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'type': 'date'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Peso en kg',
                'step': '0.1',
                'min': '0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Color de la mascota'
            }),
            'caracteristicas_especiales': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Características especiales',
                'rows': 3
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100',
                'accept': 'image/*',
                'id': 'foto_perfil_input'
            }),
            'estado_corporal': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el nombre requerido
        self.fields['nombre'].required = True
        
        # Agregar opción vacía al inicio de los selects
        self.fields['etapa_vida'].choices = [('', 'Seleccionar etapa de vida')] + list(self.fields['etapa_vida'].choices)
        self.fields['sexo'].choices = [('', 'Seleccionar sexo')] + list(self.fields['sexo'].choices)
        self.fields['estado_corporal'].choices = [('', 'Seleccionar estado corporal')] + list(self.fields['estado_corporal'].choices)