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


class BodyConditionModel(nn.Module):
    """Modelo para predicción de condición corporal"""
    def __init__(self, num_classes=3):
        super(BodyConditionModel, self).__init__()
        # Usar ResNet50 directamente como se hizo en entrenamiento
        # Asegurarnos de usar el peso correcto para la versión de PyTorch
        try:
            # Para versiones nuevas de PyTorch
            self.resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        except (AttributeError, TypeError):
            # Fallback para versiones anteriores de PyTorch
            self.resnet = models.resnet50(pretrained=True)
        
        # Reemplazar la capa fc (fully connected) exactamente como en el código de entrenamiento
        self.resnet.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.resnet(x)


class AIPredictor:
    """Servicio de predicción de IA para mascotas"""
    
    def __init__(self):
        # Modelo multi-task (raza y etapa de vida)
        self.multitask_model = None
        
        # Modelo de condición corporal
        self.body_condition_model = None
        
        # Configuración del dispositivo
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Rutas de los modelos
        self.multitask_model_path = os.path.join(settings.BASE_DIR, 'models', 'final_multitask_dog_model.pth')
        self.body_condition_model_path = os.path.join(settings.BASE_DIR, 'models', 'dog_body_condition_classifier.pth')
        
        # Definir las clases (deben coincidir con el entrenamiento)
        self.breed_classes = ['bulldog', 'chihuahua', 'golden retriever']  # alfabético
        self.stage_classes = ['adulto', 'cachorro', 'joven', 'senior']     # alfabético
        self.body_condition_classes = ['delgado', 'normal', 'obeso']       # condición corporal
        
        # Transformaciones para las imágenes (mismas para ambos modelos)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # Cargar ambos modelos al inicializar
        self._load_models()
    
    def _load_models(self):
        """Carga ambos modelos entrenados"""
        multitask_loaded = self._load_multitask_model()
        body_condition_loaded = self._load_body_condition_model()
        
        if multitask_loaded:
            logger.info("✅ Modelo multitarea cargado correctamente")
        else:
            logger.warning("⚠️ No se pudo cargar el modelo multitarea")
            
        if body_condition_loaded:
            logger.info("✅ Modelo de condición corporal cargado correctamente")
        else:
            logger.warning("⚠️ No se pudo cargar el modelo de condición corporal")
        
        return multitask_loaded or body_condition_loaded
    
    def _load_multitask_model(self):
        """Carga el modelo multitarea (raza y etapa de vida)"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.multitask_model_path):
                logger.error(f"Modelo multitarea no encontrado en: {self.multitask_model_path}")
                return False
            
            logger.info(f"Intentando cargar modelo multitarea desde: {self.multitask_model_path}")
            
            # Verificar dependencias
            try:
                import torch.nn as nn
                from torchvision import models
                logger.info("Dependencias PyTorch verificadas correctamente para modelo multitarea")
            except ImportError as e:
                logger.error(f"Error importando dependencias PyTorch para modelo multitarea: {e}")
                return False
                
            # Crear e inicializar el modelo
            try:
                self.multitask_model = MultiTaskDogModel(len(self.breed_classes), len(self.stage_classes))
                logger.info("Modelo MultiTaskDogModel creado correctamente")
            except Exception as e:
                logger.error(f"Error creando modelo MultiTaskDogModel: {e}")
                return False
            
            # Cargar los pesos del modelo entrenado
            try:
                checkpoint = torch.load(self.multitask_model_path, map_location=self.device)
                logger.info(f"Checkpoint cargado correctamente desde {self.multitask_model_path}")
            except Exception as e:
                logger.error(f"Error cargando checkpoint del modelo multitarea: {e}")
                return False
            
            # Cargar los pesos en el modelo
            try:
                if 'model_state_dict' in checkpoint:
                    self.multitask_model.load_state_dict(checkpoint['model_state_dict'])
                    logger.info("Modelo multitarea cargado correctamente (con metadatos)")
                else:
                    self.multitask_model.load_state_dict(checkpoint)
                    logger.info("Modelo multitarea cargado correctamente (formato simple)")
                
                # Preparar el modelo para inferencia
                self.multitask_model.to(self.device)
                self.multitask_model.eval()
                
                # Realizar una inferencia de prueba para verificar que funciona
                dummy_input = torch.randn(1, 3, 224, 224).to(self.device)
                with torch.no_grad():
                    breed_output, stage_output = self.multitask_model(dummy_input)
                logger.info(f"Prueba de inferencia exitosa: breed_output={breed_output.shape}, stage_output={stage_output.shape}")
                
                return True
            except Exception as e:
                logger.error(f"Error cargando pesos en el modelo multitarea: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error cargando el modelo multitarea: {e}")
            self.multitask_model = None
            # Añadimos un intento más con menos exigencias
            try:
                logger.info("Reintentando carga del modelo multitarea con manejo de errores alternativo...")
                self.multitask_model = MultiTaskDogModel(len(self.breed_classes), len(self.stage_classes))
                checkpoint = torch.load(self.multitask_model_path, map_location="cpu")
                if 'model_state_dict' in checkpoint:
                    self.multitask_model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.multitask_model.load_state_dict(checkpoint)
                self.multitask_model.eval()
                return True
            except Exception as retry_error:
                logger.error(f"Error en segundo intento de carga del modelo multitarea: {retry_error}")
                self.multitask_model = None
                return False
    
    def _load_body_condition_model(self):
        """Carga el modelo de condición corporal"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.body_condition_model_path):
                logger.error(f"Modelo de condición corporal no encontrado en: {self.body_condition_model_path}")
                return False
            
            logger.info(f"Cargando modelo de condición corporal desde: {self.body_condition_model_path}")
            
        # Verificar dependencias
            try:
                import torch.nn as nn
                from torchvision import models
                logger.info("Dependencias PyTorch verificadas correctamente para modelo de condición corporal")
            except ImportError as e:
                logger.error(f"Error importando dependencias PyTorch para modelo de condición corporal: {e}")
                return False
            
            # Crear e inicializar el modelo usando la estructura exacta de entrenamiento
            try:
                # Intentar con modo de depuración más verboso
                logger.info("Creando modelo BodyConditionModel...")
                logger.info(f"Número de clases para condición corporal: {len(self.body_condition_classes)}")
                self.body_condition_model = BodyConditionModel(len(self.body_condition_classes))
                logger.info("Modelo BodyConditionModel creado correctamente")
            except Exception as e:
                logger.error(f"Error creando modelo BodyConditionModel: {e}")
                logger.error(f"Detalles del error: {str(e.__class__.__name__)}: {str(e)}")
                return False
            
            # Cargar los pesos del modelo entrenado
            try:
                checkpoint = torch.load(self.body_condition_model_path, map_location=self.device)
                logger.info(f"Checkpoint cargado correctamente desde {self.body_condition_model_path}")
            except Exception as e:
                logger.error(f"Error cargando checkpoint del modelo: {e}")
                return False
            
            # Manejar diferentes formatos de checkpoint
            if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                # Formato directo de state_dict
                state_dict = checkpoint
            
            # Añadir más información de depuración para las claves
            logger.info(f"Claves disponibles en el checkpoint: {list(state_dict.keys())[:5]}...")
            
            # Ajustar los nombres de las claves si es necesario (para compatibilidad)
            # Utilizamos una estrategia más flexible para intentar mapear claves
            new_state_dict = {}
            for key, value in state_dict.items():
                # Si la clave ya tiene el formato correcto, úsala directamente
                if key.startswith('resnet.'):
                    new_state_dict[key] = value
                # Si la clave no tiene el prefijo 'resnet.' pero debería tenerlo
                elif any(key.startswith(prefix) for prefix in ('conv', 'bn', 'layer', 'fc', 'downsample')):
                    new_state_dict[f'resnet.{key}'] = value
                else:
                    # Mantener la clave original para otros casos
                    new_state_dict[key] = value
            
            # Cargar los pesos ajustados
            missing_keys, unexpected_keys = self.body_condition_model.load_state_dict(new_state_dict, strict=False)
            
            if missing_keys:
                logger.warning(f"Claves faltantes: {len(missing_keys)} (primeras 3: {missing_keys[:3]})")
            if unexpected_keys:
                logger.warning(f"Claves inesperadas: {len(unexpected_keys)} (primeras 3: {unexpected_keys[:3]})")
            
            logger.info("Modelo de condición corporal cargado correctamente")
            
            # Mover el modelo al dispositivo correcto
            self.body_condition_model = self.body_condition_model.to(self.device)
            self.body_condition_model.eval()
            
            # Hacer una prueba de inferencia para verificar que el modelo funciona
            try:
                logger.info("Realizando inferencia de prueba para el modelo de condición corporal")
                dummy_input = torch.randn(1, 3, 224, 224).to(self.device)
                with torch.no_grad():
                    test_output = self.body_condition_model(dummy_input)
                    logger.info(f"Prueba exitosa. Output shape: {test_output.shape}")
                    
                    # Verificar que el modelo produce salidas válidas
                    test_probs = torch.softmax(test_output, dim=1)
                    test_pred = torch.argmax(test_probs, dim=1).item()
                    logger.info(f"Predicción de prueba: índice={test_pred}, clase={self.body_condition_classes[test_pred]}")
                    
                return True
            except Exception as test_error:
                logger.error(f"Error en la prueba de inferencia del modelo de condición corporal: {test_error}")
                return False
            
        except Exception as e:
            logger.error(f"Error cargando el modelo de condición corporal: {e}")
            
            # Añadimos un intento más con menos exigencias
            try:
                logger.info("Reintentando carga del modelo de condición corporal con manejo de errores alternativo...")
                self.body_condition_model = BodyConditionModel(len(self.body_condition_classes))
                checkpoint = torch.load(self.body_condition_model_path, map_location="cpu")
                if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                else:
                    state_dict = checkpoint
                    
                # Intento sin ajustar claves - más sencillo
                self.body_condition_model.load_state_dict(state_dict, strict=False)
                self.body_condition_model.eval()
                
                # Probar una inferencia simple para verificar que el modelo funciona
                dummy_input = torch.randn(1, 3, 224, 224).to("cpu")  # Usar CPU por seguridad
                with torch.no_grad():
                    test_output = self.body_condition_model(dummy_input)
                logger.info(f"Prueba de inferencia básica exitosa en segundo intento")
                
                # Mover a dispositivo correcto después de verificar que funciona
                self.body_condition_model = self.body_condition_model.to(self.device)
                
                return True
            except Exception as retry_error:
                logger.error(f"Error en segundo intento de carga del modelo de condición corporal: {retry_error}")
                self.body_condition_model = None
                return False
    
    def predict_from_image_file(self, image_file):
        """
        Predice raza, etapa de vida y condición corporal desde un archivo de imagen Django
        
        Args:
            image_file: Archivo de imagen Django (UploadedFile)
            
        Returns:
            dict: Diccionario con las predicciones y confianzas
        """
        # Verificar estado de modelos y registrar para diagnóstico
        logger.info(f"Estado de modelos antes de predicción: multitarea={self.multitask_model is not None}, condición corporal={self.body_condition_model is not None}")
        
        if not self.multitask_model and not self.body_condition_model:
            logger.error("Ambos modelos no están disponibles para predicción")
            return {
                'success': False,
                'error': 'Ningún modelo disponible'
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
        Predice raza, etapa de vida y condición corporal desde una ruta de imagen
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            dict: Diccionario con las predicciones y confianzas
        """
        if not self.multitask_model and not self.body_condition_model:
            return {
                'success': False,
                'error': 'Ningún modelo disponible'
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
        Realiza la predicción desde una imagen PIL usando ambos modelos
        
        Args:
            image: Imagen PIL
            
        Returns:
            dict: Diccionario con las predicciones y confianzas
        """
        try:
            # Añadir más información de depuración
            logger.debug(f"Iniciando predicción de imagen. Dispositivo: {self.device}")
            logger.debug(f"Modelos cargados: Multitarea={self.multitask_model is not None}, Condición corporal={self.body_condition_model is not None}")
            
            # Verificar que la imagen es válida
            if not isinstance(image, Image.Image):
                logger.error(f"Tipo de imagen incorrecto: {type(image)}")
                return {
                    'success': False,
                    'error': f'Tipo de imagen incorrecto: {type(image)}'
                }
            
            # Aplicar transformaciones
            try:
                input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            except Exception as e:
                logger.error(f"Error al transformar imagen: {e}")
                return {
                    'success': False,
                    'error': f'Error al transformar imagen: {str(e)}'
                }
            
            predictions = {}
            
            # Predicción con modelo multitarea (raza y etapa de vida)
            if self.multitask_model:
                try:
                    logger.info("Realizando predicción con modelo multitarea...")
                    with torch.no_grad():
                        breed_outputs, stage_outputs = self.multitask_model(input_tensor)
                        
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
                        
                        # Añadir resultados al diccionario de predicciones
                        predictions['breed'] = {
                            'predicted': predicted_breed,
                            'confidence': breed_confidence,
                            'confidence_level': breed_confidence_level,
                            'all_probabilities': breed_probabilities
                        }
                        
                        predictions['stage'] = {
                            'predicted': predicted_stage,
                            'confidence': stage_confidence,
                            'confidence_level': stage_confidence_level,
                            'all_probabilities': stage_probabilities
                        }
                        
                        logger.info("Predicciones multitarea añadidas correctamente al diccionario de resultados")
                        
                        logger.info(f"Predicción multitarea exitosa: raza={predicted_breed}, etapa={predicted_stage}")
                except Exception as e:
                    logger.error(f"Error en predicción con modelo multitarea: {e}")
                    logger.error(f"Detalles del error: {str(e.__class__.__name__)}: {str(e)}")
                    # Continuar con el siguiente modelo si este falla
            else:
                logger.warning("Modelo multitarea no disponible - no se realizarán predicciones de raza ni etapa de vida")
                    
            
            # Predicción con modelo de condición corporal
            if self.body_condition_model:
                try:
                    logger.info("Realizando predicción de condición corporal...")
                    # Asegurar que el modelo está en modo evaluación
                    self.body_condition_model.eval()
                    
                    # Verificar que esté en el dispositivo correcto
                    if next(self.body_condition_model.parameters()).device != self.device:
                        logger.info(f"Moviendo modelo de condición corporal al dispositivo {self.device}")
                        self.body_condition_model = self.body_condition_model.to(self.device)
                    
                    with torch.no_grad():
                        # Log detallado para diagnóstico
                        logger.debug(f"Ejecutando forward pass del modelo de condición corporal. Input shape: {input_tensor.shape}")
                        
                        body_outputs = self.body_condition_model(input_tensor)
                        logger.debug(f"Output del modelo: shape={body_outputs.shape}")
                        
                        # Aplicar softmax para obtener probabilidades
                        body_probs = torch.softmax(body_outputs, dim=1)
                        logger.debug(f"Probabilidades después de softmax: {body_probs}")
                        
                        # Obtener la predicción
                        body_pred_idx = torch.argmax(body_probs, dim=1).item()
                        logger.debug(f"Índice predicho: {body_pred_idx}, clase: {self.body_condition_classes[body_pred_idx]}")
                        
                        # Obtener la probabilidad máxima
                        body_confidence = body_probs[0][body_pred_idx].item()
                        logger.debug(f"Confianza de la predicción: {body_confidence:.4f}")
                        
                        # Mapear índice a nombre
                        predicted_body_condition = self.body_condition_classes[body_pred_idx]
                        
                        # Preparar todas las probabilidades
                        body_probabilities = {}
                        for i, condition in enumerate(self.body_condition_classes):
                            body_probabilities[condition] = body_probs[0][i].item()
                        
                        # Determinar nivel de confianza
                        body_confidence_level = self._get_confidence_level(body_confidence)
                        
                        predictions['body_condition'] = {
                            'predicted': predicted_body_condition,
                            'confidence': body_confidence,
                            'confidence_level': body_confidence_level,
                            'all_probabilities': body_probabilities
                        }
                        
                        logger.info(f"Predicción de condición corporal exitosa: {predicted_body_condition} con confianza {body_confidence:.2f}")
                except Exception as e:
                    logger.error(f"Error en predicción con modelo de condición corporal: {e}")
                    logger.error(f"Detalles del error: {str(e.__class__.__name__)}: {str(e)}")
                    
                    # Intentar nuevamente con un enfoque más simple como último recurso
                    try:
                        logger.info("Reintentando predicción de condición corporal con enfoque simplificado...")
                        # Mover modelo a CPU por si el problema es con GPU
                        simple_model = self.body_condition_model.to("cpu")
                        simple_input = self.transform(image).unsqueeze(0).to("cpu")
                        
                        with torch.no_grad():
                            simple_output = simple_model(simple_input)
                            simple_probs = torch.softmax(simple_output, dim=1)
                            simple_pred_idx = torch.argmax(simple_probs, dim=1).item()
                            simple_confidence = simple_probs[0][simple_pred_idx].item()
                            predicted_body_condition = self.body_condition_classes[simple_pred_idx]
                            
                            # Preparar probabilidades
                            body_probabilities = {}
                            for i, condition in enumerate(self.body_condition_classes):
                                body_probabilities[condition] = simple_probs[0][i].item()
                            
                            body_confidence_level = self._get_confidence_level(simple_confidence)
                            predictions['body_condition'] = {
                                'predicted': predicted_body_condition,
                                'confidence': simple_confidence,
                                'confidence_level': body_confidence_level,
                                'all_probabilities': body_probabilities,
                                'fallback_mode': True
                            }
                            logger.info(f"Reintento exitoso de predicción de condición corporal: {predicted_body_condition}")
                    except Exception as retry_e:
                        logger.error(f"Error en reintento de predicción de condición corporal: {retry_e}")
                        # Continuar sin la predicción de condición corporal
            else:
                logger.warning("Modelo de condición corporal no disponible - no se realizarán predicciones de condición corporal")
            
            # Verificamos si tenemos al menos una predicción válida
            if any(key in predictions for key in ['breed', 'stage', 'body_condition']):
                # Registrar qué modelos han producido predicciones
                logger.info(f"Predicciones disponibles: breed={('breed' in predictions)}, " +
                           f"stage={('stage' in predictions)}, " +
                           f"body_condition={('body_condition' in predictions)}")
                
                # Verificar especialmente el modelo de condición corporal
                if 'body_condition' not in predictions and self.body_condition_model is not None:
                    logger.warning("El modelo de condición corporal está cargado pero no produjo predicciones")
                
                return {
                    'success': True,
                    'predictions': predictions
                }
            else:
                # Si llegamos aquí, intentamos reiniciar el predictor y cargar de nuevo los modelos
                logger.warning("Ninguna predicción disponible - intentando reiniciar modelos")
                try:
                    # Reintentar cargar los modelos
                    if not self.multitask_model:
                        self._load_multitask_model()
                    if not self.body_condition_model:
                        self._load_body_condition_model()
                        
                    # Si después del reintento seguimos sin modelos, fallamos
                    if not self.multitask_model and not self.body_condition_model:
                        return {
                            'success': False,
                            'error': 'Ningún modelo pudo hacer predicciones'
                        }
                        
                    # Si tenemos al menos un modelo, intentamos de nuevo la predicción
                    if self.multitask_model or self.body_condition_model:
                        logger.info("Modelos recargados, reintentando predicción")
                        # Si aquí tenemos al menos algún modelo, devolvemos lo que tengamos
                        # aunque sea incompleto
                        return {
                            'success': True,
                            'predictions': predictions if predictions else {'partial': True, 'message': 'Predicción parcial'}
                        }
                except Exception as reload_error:
                    logger.error(f"Error al reintentar carga de modelos: {reload_error}")
                    
                # Si llegamos aquí, realmente no pudimos hacer predicciones
                return {
                    'success': False,
                    'error': 'Ningún modelo pudo hacer predicciones'
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
    
    def get_body_condition_choices_for_django(self):
        """Retorna las opciones de condición corporal en formato Django choices"""
        choices = []
        for condition in self.body_condition_classes:
            # Capitalizar para mostrar mejor
            display_name = condition.capitalize()
            choices.append((condition, display_name))
        return choices
    
    def get_body_condition_display_name(self, condition_internal):
        """Convierte el nombre interno de condición corporal a nombre para mostrar"""
        condition_mapping = {
            'delgado': 'Delgado',
            'normal': 'Normal (Ideal)',
            'obeso': 'Sobrepeso/Obeso'
        }
        return condition_mapping.get(condition_internal, condition_internal.capitalize())
    
    def get_body_condition_description(self, condition_internal):
        """Obtiene la descripción de la condición corporal"""
        descriptions = {
            'delgado': 'El canino presenta bajo peso corporal. Se recomienda evaluación veterinaria.',
            'normal': 'El canino presenta un peso corporal ideal. Mantener rutina de alimentación y ejercicio.',
            'obeso': 'El canino presenta sobrepeso u obesidad. Se recomienda plan de reducción de peso supervisado.'
        }
        return descriptions.get(condition_internal, 'Condición corporal no determinada.')


# Instancia global del predictor con manejo de errores mejorado
try:
    predictor = AIPredictor()
except Exception as e:
    logger.error(f"Error crítico inicializando predictor global: {e}")
    # Crear un predictor en modo seguro que se inicializará bajo demanda
    class SafePredictor:
        def __init__(self):
            self._real_predictor = None
            self._init_attempts = 0
            self._max_attempts = 3
            
        def _ensure_predictor(self):
            if self._real_predictor is None and self._init_attempts < self._max_attempts:
                try:
                    logger.info(f"Intento {self._init_attempts + 1} de inicializar predictor bajo demanda")
                    self._real_predictor = AIPredictor()
                    logger.info("Predictor inicializado correctamente bajo demanda")
                except Exception as init_error:
                    logger.error(f"Error inicializando predictor bajo demanda: {init_error}")
                self._init_attempts += 1
            return self._real_predictor
                
        def predict_from_image_file(self, *args, **kwargs):
            predictor = self._ensure_predictor()
            if predictor:
                return predictor.predict_from_image_file(*args, **kwargs)
            return {'success': False, 'error': 'Servicio de predicción no disponible temporalmente'}
            
        def predict_from_image_path(self, *args, **kwargs):
            predictor = self._ensure_predictor()
            if predictor:
                return predictor.predict_from_image_path(*args, **kwargs)
            return {'success': False, 'error': 'Servicio de predicción no disponible temporalmente'}
            
        def get_breed_choices_for_django(self):
            predictor = self._ensure_predictor()
            if predictor:
                return predictor.get_breed_choices_for_django()
            return [('no_disponible', 'No disponible')]
            
        def get_stage_choices_for_django(self):
            predictor = self._ensure_predictor()
            if predictor:
                return predictor.get_stage_choices_for_django()
            return [('no_disponible', 'No disponible')]
            
        def get_body_condition_choices_for_django(self):
            predictor = self._ensure_predictor()
            if predictor:
                return predictor.get_body_condition_choices_for_django()
            return [('no_disponible', 'No disponible')]
            
    # Usar el predictor seguro en caso de error
    predictor = SafePredictor()