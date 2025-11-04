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
                'required': True,
                'minlength': '2',
                'maxlength': '50'
            }),
            'raza': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Raza (se puede predecir automáticamente)',
                'id': 'id_raza',
                'maxlength': '100'
            }),
            'etapa_vida': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_etapa_vida',
                'required': True
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Edad',
                'min': '0',
                'max': '30',
                'step': '1',
                'required': True,
                'id': 'id_edad'
            }),
            'edad_unidad': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_edad_unidad'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Sexo de la mascota',
                'required': True
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'max': 'today',
                'required': True
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Peso en kg',
                'step': '0.1',
                'min': '0.1',
                'max': '200',
                'required': True
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Color de la mascota',
                'maxlength': '50',
                'required': True
            }),
            'caracteristicas_especiales': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Características especiales',
                'rows': 3,
                'maxlength': '500',
                'required': True
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'id': 'foto_perfil_input',
                'required': True
            }),
            'estado_corporal': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer campos obligatorios
        self.fields['nombre'].required = True
        self.fields['color'].required = True
        self.fields['estado_corporal'].required = True
        self.fields['fecha_nacimiento'].required = True
        self.fields['caracteristicas_especiales'].required = True
        
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