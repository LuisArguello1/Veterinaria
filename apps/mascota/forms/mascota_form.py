from django import forms
from apps.mascota.models import Mascota


class MascotaCreateForm(forms.ModelForm):
    """
    Formulario para el registro de nuevas mascotas.
    Solo puede ser usado por usuarios con rol OWNER o ADMIN.
    """
    
    class Meta:
        model = Mascota
        fields = [
            'nombre',
            'raza',
            'sexo',
            'fecha_nacimiento',
            'peso',
            'color',
            'etapa_vida',
            'estado_corporal',
            'caracteristicas_especiales',
            'foto_perfil'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
                'placeholder': 'Ej: Firulais',
                'required': True
            }),
            'raza': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
                'placeholder': 'Ej: Labrador Retriever'
            }),
            'sexo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
                'placeholder': 'Ej: 15.5',
                'step': '0.01',
                'min': '0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
                'placeholder': 'Ej: Negro con manchas blancas'
            }),
            'etapa_vida': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
            }),
            'estado_corporal': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
            }),
            'caracteristicas_especiales': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
                'placeholder': 'Ej: Cicatriz en la pata trasera izquierda, alergia al pollo',
                'rows': 4
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100',
                'accept': 'image/*'
            })
        }
        
        labels = {
            'nombre': 'Nombre de la mascota',
            'raza': 'Raza / Especie',
            'sexo': 'Sexo',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'peso': 'Peso (kg)',
            'color': 'Color / Pelaje',
            'etapa_vida': 'Etapa de vida',
            'estado_corporal': 'Estado corporal',
            'caracteristicas_especiales': 'Características especiales',
            'foto_perfil': 'Foto de perfil'
        }
        
        help_texts = {
            'nombre': 'Nombre por el cual se identifica a la mascota',
            'raza': 'Raza o especie de la mascota (opcional)',
            'fecha_nacimiento': 'Fecha aproximada de nacimiento (opcional)',
            'peso': 'Peso actual en kilogramos (opcional)',
            'caracteristicas_especiales': 'Marcas, cicatrices, alergias, comportamientos especiales, etc. (opcional)',
            'foto_perfil': 'Foto principal de la mascota (opcional, se puede agregar después)'
        }
    
    def clean_nombre(self):
        """Validar que el nombre no esté vacío y tenga una longitud razonable"""
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre de la mascota es obligatorio.')
        if len(nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        if len(nombre) > 120:
            raise forms.ValidationError('El nombre no puede exceder los 120 caracteres.')
        return nombre
    
    def clean_peso(self):
        """Validar que el peso sea un valor razonable"""
        peso = self.cleaned_data.get('peso')
        if peso is not None:
            if peso < 0:
                raise forms.ValidationError('El peso no puede ser negativo.')
            if peso > 500:  # Peso máximo razonable para animales domésticos
                raise forms.ValidationError('El peso parece ser demasiado alto. Verifique el valor.')
        return peso
    
    def clean_foto_perfil(self):
        """Validar el tamaño y tipo de la foto de perfil"""
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            # Validar tamaño (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede exceder los 5 MB.')
            
            # Validar tipo de archivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            import os
            ext = os.path.splitext(foto.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Formato de imagen no válido. Use: {", ".join(valid_extensions)}'
                )
        return foto
