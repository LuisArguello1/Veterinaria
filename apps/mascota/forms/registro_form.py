# apps/mascota/forms/registro_form.py
from django import forms
from django.core.exceptions import ValidationError
from apps.mascota.models import Mascota
from apps.mascota.services.ai_predictor import predictor


class MascotaRegistroForm(forms.ModelForm):
    """Formulario para registro de mascotas con predicción de IA"""
    
    # Campos adicionales para predicciones
    usar_prediccion_raza = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'usar_prediccion_raza'
        })
    )
    
    usar_prediccion_etapa = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'usar_prediccion_etapa'
        })
    )
    
    class Meta:
        model = Mascota
        fields = [
            'nombre', 'raza', 'etapa_vida', 'edad', 'edad_unidad',
            'sexo', 'fecha_nacimiento', 'peso', 'color',
            'caracteristicas_especiales', 'foto_perfil', 'estado_corporal'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de la mascota',
                'required': True
            }),
            'raza': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Raza (se puede predecir automáticamente)',
                'id': 'id_raza'
            }),
            'etapa_vida': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_etapa_vida'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Edad',
                'min': '0'
            }),
            'edad_unidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Sexo de la mascota'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Peso en kg',
                'step': '0.1',
                'min': '0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Color de la mascota'
            }),
            'caracteristicas_especiales': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Características especiales',
                'rows': 3
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'id': 'foto_perfil_input'
            }),
            'estado_corporal': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el nombre requerido
        self.fields['nombre'].required = True
        
        # Personalizar choices para etapa_vida usando las del modelo de IA
        ai_stage_choices = predictor.get_stage_choices_for_django()
        # Agregar opción vacía al inicio
        stage_choices = [('', 'Seleccionar etapa de vida')] + ai_stage_choices
        self.fields['etapa_vida'].choices = stage_choices
    
    def clean_foto_perfil(self):
        """Validación personalizada para la foto de perfil"""
        foto = self.cleaned_data.get('foto_perfil')
        
        if foto:
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
        
        if peso is not None and peso <= 0:
            raise ValidationError("El peso debe ser mayor a 0.")
        
        return peso
    
    def clean_edad(self):
        """Validación para la edad"""
        edad = self.cleaned_data.get('edad')
        
        if edad is not None and edad < 0:
            raise ValidationError("La edad no puede ser negativa.")
        
        return edad
    
    def get_ai_predictions(self):
        """
        Obtiene las predicciones de IA para la foto de perfil
        Retorna None si no hay foto o si hay errores
        """
        foto = self.cleaned_data.get('foto_perfil') or self.files.get('foto_perfil')
        
        if not foto:
            return None
        
        try:
            # Usar el predictor para obtener las predicciones
            predictions = predictor.predict_from_image_file(foto)
            
            if predictions['success']:
                return predictions['predictions']
            else:
                return None
                
        except Exception as e:
            print(f"Error en predicción de IA: {e}")
            return None
    
    def apply_ai_predictions(self, predictions):
        """
        Aplica las predicciones de IA a los campos del formulario
        """
        if not predictions:
            return
        
        # Aplicar predicción de raza si el usuario la acepta
        usar_raza = self.cleaned_data.get('usar_prediccion_raza', False)
        if usar_raza and 'breed' in predictions:
            predicted_breed = predictions['breed']['predicted']
            # Mapear el nombre interno a un nombre más amigable
            breed_mapping = {
                'bulldog': 'Bulldog',
                'chihuahua': 'Chihuahua', 
                'golden retriever': 'Golden Retriever'
            }
            self.cleaned_data['raza'] = breed_mapping.get(predicted_breed, predicted_breed.title())
        
        # Aplicar predicción de etapa de vida si el usuario la acepta
        usar_etapa = self.cleaned_data.get('usar_prediccion_etapa', False)
        if usar_etapa and 'stage' in predictions:
            predicted_stage = predictions['stage']['predicted']
            self.cleaned_data['etapa_vida'] = predicted_stage