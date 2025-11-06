from django import forms
from django.core.exceptions import ValidationError
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
    
    def clean_foto_perfil(self):
        """Validación personalizada para la foto de perfil"""
        foto = self.cleaned_data.get('foto_perfil')
        
        # Si no hay foto o es False (campo vacío), retornar como está
        if not foto or foto is False:
            return foto
        
        # Solo validar si es un archivo nuevo (UploadedFile tiene content_type y size)
        if hasattr(foto, 'content_type') and hasattr(foto, 'size'):
            # Validar tamaño (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError("La imagen no puede ser mayor a 5MB.")
            
            # Validar tipo de archivo
            if not foto.content_type.startswith('image/'):
                raise ValidationError("El archivo debe ser una imagen.")
        
        return foto
    
    def clean_peso(self):
        """Validación para el peso"""
        peso = self.cleaned_data.get('peso')
        
        if peso is None:
            raise ValidationError("El peso es obligatorio.")
        
        if peso <= 0:
            raise ValidationError("El peso debe ser mayor a 0.")
        
        if peso < 0.1:
            raise ValidationError("El peso debe ser al menos 0.1 kg.")
        
        if peso > 200:
            raise ValidationError("El peso no puede ser mayor a 200 kg.")
        
        return peso
    
    def clean_edad(self):
        """Validación para la edad"""
        edad = self.cleaned_data.get('edad')
        
        if edad is None:
            raise ValidationError("La edad es obligatoria.")
        
        if edad < 0:
            raise ValidationError("La edad no puede ser negativa.")
        
        if edad == 0:
            raise ValidationError("La edad debe ser mayor a 0.")
        
        if edad > 30:
            raise ValidationError("La edad no puede ser mayor a 30.")
        
        return edad
    
    def clean(self):
        """Validación general del formulario, incluyendo fecha de nacimiento vs edad"""
        cleaned_data = super().clean()
        
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        edad = cleaned_data.get('edad')
        edad_unidad = cleaned_data.get('edad_unidad')
        
        if fecha_nacimiento and edad:
            from datetime import date
            
            # Calcular edad desde fecha de nacimiento
            hoy = date.today()
            edad_calculada_anios = hoy.year - fecha_nacimiento.year
            mes_actual = hoy.month
            mes_nacimiento = fecha_nacimiento.month
            
            # Ajustar si aún no ha cumplido años este año
            if mes_actual < mes_nacimiento or (mes_actual == mes_nacimiento and hoy.day < fecha_nacimiento.day):
                edad_calculada_anios -= 1
            
            # Calcular meses adicionales
            meses_adicionales = mes_actual - mes_nacimiento
            if meses_adicionales < 0:
                meses_adicionales += 12
            
            edad_calculada_total_anios = edad_calculada_anios + (meses_adicionales / 12)
            
            # Convertir edad ingresada a años para comparación
            edad_ingresada_en_anios = edad
            if edad_unidad == 'meses':
                edad_ingresada_en_anios = edad / 12
            
            # Calcular diferencia
            diferencia = abs(edad_ingresada_en_anios - edad_calculada_total_anios)
            
            # Si la diferencia es mayor a 3 meses (0.25 años), mostrar error
            if diferencia > 0.25:
                texto_edad_ingresada = f"{edad} {'año' if edad == 1 else 'años'}" if edad_unidad == 'años' else f"{edad} {'mes' if edad == 1 else 'meses'}"
                texto_edad_calculada = f"{edad_calculada_anios} {'año' if edad_calculada_anios == 1 else 'años'} y {meses_adicionales} {'mes' if meses_adicionales == 1 else 'meses'}"
                
                raise ValidationError(
                    f"La edad ingresada ({texto_edad_ingresada}) no coincide con la fecha de nacimiento ({texto_edad_calculada}). "
                    f"Por favor verifica que ambos datos sean correctos."
                )
        
        return cleaned_data