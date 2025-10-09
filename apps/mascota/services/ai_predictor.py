# apps/mascota/services/ai_predictor.py
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MultiTaskDogModel(nn.Module):
    """Modelo multi-task para predicción de raza y etapa de vida"""
    def __init__(self, num_breeds, num_stages):
        super(MultiTaskDogModel, self).__init__()
        
        # Backbone pre-entrenado (igual que en el entrenamiento)
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        
        # Remover la última capa (igual que en entrenamiento)
        self.features = nn.Sequential(*list(self.backbone.children())[:-1])
        
        # Cabezas para cada tarea
        self.breed_classifier = nn.Linear(512, num_breeds)
        self.stage_classifier = nn.Linear(512, num_stages)
        
    def forward(self, x):
        # Extraer características
        features = self.features(x)
        features = features.view(features.size(0), -1)
        
        # Predicciones para cada tarea
        breed_output = self.breed_classifier(features)
        stage_output = self.stage_classifier(features)
        
        return breed_output, stage_output


class AIPredictor:
    """Servicio de predicción de IA para mascotas"""
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'final_multitask_dog_model.pth')
        
        # Definir las clases (deben coincidir con el entrenamiento)
        self.breed_classes = ['bulldog', 'chihuahua', 'golden retriever']  # alfabético
        self.stage_classes = ['adulto', 'cachorro', 'joven', 'senior']     # alfabético
        
        # Transformaciones para las imágenes
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # Cargar el modelo al inicializar
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo entrenado"""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Modelo no encontrado en: {self.model_path}")
                return False
                
            # Crear e inicializar el modelo
            self.model = MultiTaskDogModel(len(self.breed_classes), len(self.stage_classes))
            
            # Cargar los pesos del modelo entrenado
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
                logger.info("Modelo cargado correctamente (con metadatos)")
            else:
                self.model.load_state_dict(checkpoint)
                logger.info("Modelo cargado correctamente (formato simple)")
            
            self.model.to(self.device)
            self.model.eval()
            return True
            
        except Exception as e:
            logger.error(f"Error cargando el modelo: {e}")
            self.model = None
            return False
    
    def predict_from_image_file(self, image_file):
        """
        Predice raza y etapa de vida desde un archivo de imagen Django
        
        Args:
            image_file: Archivo de imagen Django (UploadedFile)
            
        Returns:
            dict: Diccionario con las predicciones y confianzas
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Modelo no disponible'
            }
        
        try:
            # Abrir la imagen desde el archivo
            image = Image.open(image_file).convert("RGB")
            return self._predict_from_pil_image(image)
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return {
                'success': False,
                'error': f'Error procesando imagen: {str(e)}'
            }
    
    def predict_from_image_path(self, image_path):
        """
        Predice raza y etapa de vida desde una ruta de imagen
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            dict: Diccionario con las predicciones y confianzas
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Modelo no disponible'
            }
        
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Imagen no encontrada'
                }
            
            # Abrir la imagen
            image = Image.open(image_path).convert("RGB")
            return self._predict_from_pil_image(image)
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return {
                'success': False,
                'error': f'Error procesando imagen: {str(e)}'
            }
    
    def _predict_from_pil_image(self, image):
        """
        Realiza la predicción desde una imagen PIL
        
        Args:
            image: Imagen PIL
            
        Returns:
            dict: Diccionario con las predicciones y confianzas
        """
        try:
            # Aplicar transformaciones
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Hacer predicción
            with torch.no_grad():
                breed_outputs, stage_outputs = self.model(input_tensor)
                
                # Aplicar softmax para obtener probabilidades
                breed_probs = torch.softmax(breed_outputs, dim=1)
                stage_probs = torch.softmax(stage_outputs, dim=1)
                
                # Obtener las predicciones
                breed_pred_idx = torch.argmax(breed_probs, dim=1).item()
                stage_pred_idx = torch.argmax(stage_probs, dim=1).item()
                
                # Obtener las probabilidades máximas
                breed_confidence = breed_probs[0][breed_pred_idx].item()
                stage_confidence = stage_probs[0][stage_pred_idx].item()
                
                # Mapear índices a nombres
                predicted_breed = self.breed_classes[breed_pred_idx]
                predicted_stage = self.stage_classes[stage_pred_idx]
                
                # Preparar todas las probabilidades
                breed_probabilities = {}
                for i, breed in enumerate(self.breed_classes):
                    breed_probabilities[breed] = breed_probs[0][i].item()
                
                stage_probabilities = {}
                for i, stage in enumerate(self.stage_classes):
                    stage_probabilities[stage] = stage_probs[0][i].item()
                
                # Determinar nivel de confianza
                breed_confidence_level = self._get_confidence_level(breed_confidence)
                stage_confidence_level = self._get_confidence_level(stage_confidence)
                
                return {
                    'success': True,
                    'predictions': {
                        'breed': {
                            'predicted': predicted_breed,
                            'confidence': breed_confidence,
                            'confidence_level': breed_confidence_level,
                            'all_probabilities': breed_probabilities
                        },
                        'stage': {
                            'predicted': predicted_stage,
                            'confidence': stage_confidence,
                            'confidence_level': stage_confidence_level,
                            'all_probabilities': stage_probabilities
                        }
                    }
                }
                
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {
                'success': False,
                'error': f'Error en predicción: {str(e)}'
            }
    
    def _get_confidence_level(self, confidence):
        """Determina el nivel de confianza basado en el valor numérico"""
        if confidence > 0.8:
            return 'high'
        elif confidence > 0.6:
            return 'medium'
        else:
            return 'low'
    
    def get_breed_choices_for_django(self):
        """Retorna las opciones de raza en formato Django choices"""
        choices = []
        for breed in self.breed_classes:
            # Capitalizar para mostrar mejor
            display_name = breed.replace('_', ' ').title()
            choices.append((breed, display_name))
        return choices
    
    def get_stage_choices_for_django(self):
        """Retorna las opciones de etapa en formato Django choices"""
        choices = []
        for stage in self.stage_classes:
            # Capitalizar para mostrar mejor
            display_name = stage.capitalize()
            choices.append((stage, display_name))
        return choices


# Instancia global del predictor
predictor = AIPredictor()