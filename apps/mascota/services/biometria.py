# apps/mascota/services/biometria.py
import os
import time
import pickle
import numpy as np
import logging
from typing import List, Dict, Tuple, Union, Optional
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

# Importaciones condicionales para evitar errores al iniciar Django si no están instaladas
try:
    import cv2
    import torch
    import torchvision
    from torchvision import transforms
    from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
    from torchvision.models import resnet50, ResNet50_Weights
    from torchvision.models.feature_extraction import create_feature_extractor
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.svm import SVC
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
    DEPS_INSTALLED = True
except ImportError:
    DEPS_INSTALLED = False
    logging.warning("Dependencias de biometría no instaladas. Instala: torch, torchvision, scikit-learn, opencv-python")

# Configuración de logging
logger = logging.getLogger(__name__)

# Definiciones para facilitar tipado y documentación
ImageArray = np.ndarray  # Imagen como array numpy
EmbeddingVector = np.ndarray  # Vector de características

class BiometriaService:
    """
    Servicio para manejar la biometría de mascotas:
    - Extracción de características (embeddings)
    - Entrenamiento del modelo clasificador
    - Predicción de identidad de mascotas
    """
    
    def __init__(self, modelo_extractor: str = 'efficientnet_b0'):
        """
        Inicializa el servicio de biometría.
        
        Args:
            modelo_extractor: Nombre del modelo a usar como extractor ('efficientnet_b0', 'resnet50', etc.)
        """
        if not DEPS_INSTALLED:
            logger.error("No se pueden inicializar modelos: faltan dependencias")
            return
            
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.modelo_extractor = modelo_extractor
        self.feature_extractor = None
        self.preprocess = None
        self.clasificador = None
        self.dimension_embeddings = None
        
        # Inicializar el extractor de características
        self._initialize_feature_extractor()
    
    def _initialize_feature_extractor(self):
        """Inicializa el modelo de extracción de características (embeddings)"""
        if self.modelo_extractor == 'efficientnet_b0':
            weights = EfficientNet_B0_Weights.DEFAULT
            model = efficientnet_b0(weights=weights)
            self.dimension_embeddings = 1280  # Dimensión del vector de EfficientNet B0
            
            # Transformaciones requeridas por el modelo
            self.preprocess = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            # Crear extractor de características (quita la capa de clasificación)
            self.feature_extractor = create_feature_extractor(
                model, 
                return_nodes=['flatten']
            )
            
        elif self.modelo_extractor == 'resnet50':
            weights = ResNet50_Weights.DEFAULT
            model = resnet50(weights=weights)
            self.dimension_embeddings = 2048  # Dimensión del vector de ResNet50
            
            self.preprocess = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            self.feature_extractor = create_feature_extractor(
                model, 
                return_nodes=['flatten']
            )
        else:
            raise ValueError(f"Modelo extractor no soportado: {self.modelo_extractor}")
        
        # Mover modelo a GPU si está disponible
        self.feature_extractor = self.feature_extractor.to(self.device)
        self.feature_extractor.eval()
        
        logger.info(f"Extractor de características inicializado: {self.modelo_extractor} en {self.device}")
    
    def procesar_imagen(self, ruta_imagen: Union[str, Path]) -> ImageArray:
        """
        Procesa una imagen para prepararla para el análisis biométrico
        
        Args:
            ruta_imagen: Ruta al archivo de imagen
            
        Returns:
            Imagen como array numpy procesada
        """
        # Cargar imagen con OpenCV
        img = cv2.imread(str(ruta_imagen))
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen: {ruta_imagen}")
        
        # Convertir de BGR a RGB (OpenCV usa BGR por defecto)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        return img
    
    def detectar_mascota(self, img: ImageArray) -> Tuple[ImageArray, Optional[Tuple[int, int, int, int]]]:
        """
        Detecta una mascota en la imagen usando Haar Cascades de OpenCV
        
        Args:
            img: Imagen como array numpy
            
        Returns:
            Tuple con (imagen recortada, coordenadas del recorte o None si no se detecta)
        """
        # Esta es una implementación básica - en un sistema real sería mejor usar
        # un modelo especializado en detectar mascotas (perros/gatos)
        
        # Convertir a escala de grises para la detección
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Intentar detectar con un clasificador Haar Cascade para perros
        # (Esto requiere tener un archivo XML de cascada para mascotas)
        try:
            # Esto es un ejemplo - necesitarías un archivo de cascada adecuado
            cascade_path = os.path.join(settings.BASE_DIR, 'models', 'dog-cascade_40x40_rev2.xml')
            if os.path.exists(cascade_path):
                classifier = cv2.CascadeClassifier(cascade_path)
                detections = classifier.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                
                if len(detections) > 0:
                    # Tomar la detección más grande
                    x, y, w, h = sorted(detections, key=lambda d: d[2]*d[3], reverse=True)[0]
                    
                    # Agrandar un poco el área para incluir toda la cara
                    factor = 0.2
                    x_new = max(0, int(x - w * factor))
                    y_new = max(0, int(y - h * factor))
                    w_new = int(w * (1 + 2 * factor))
                    h_new = int(h * (1 + 2 * factor))
                    
                    # Asegurar que no exceda los límites de la imagen
                    h_img, w_img = img.shape[:2]
                    x_new = min(x_new, w_img - 1)
                    y_new = min(y_new, h_img - 1)
                    w_new = min(w_new, w_img - x_new)
                    h_new = min(h_new, h_img - y_new)
                    
                    # Recortar imagen
                    recorte = img[y_new:y_new+h_new, x_new:x_new+w_new]
                    return recorte, (x_new, y_new, w_new, h_new)
        except Exception as e:
            logger.warning(f"Error en detección de mascota: {e}")
            
        # Si no se detecta, retornar la imagen original
        return img, None
    
    def extraer_embedding(self, img: ImageArray) -> EmbeddingVector:
        """
        Extrae el vector de características (embedding) de una imagen
        
        Args:
            img: Imagen como array numpy
            
        Returns:
            Vector de características (embedding)
        """
        if not DEPS_INSTALLED:
            raise ImportError("No se pueden extraer embeddings: faltan dependencias")
            
        if self.feature_extractor is None:
            self._initialize_feature_extractor()
        
        # Preprocesar imagen
        img_tensor = self.preprocess(img)
        img_tensor = img_tensor.unsqueeze(0)  # Añadir dimensión de batch
        img_tensor = img_tensor.to(self.device)
        
        # Extraer características
        with torch.no_grad():
            features = self.feature_extractor(img_tensor)
        
        # Obtener el tensor y convertirlo a numpy
        feature_tensor = features['flatten']
        embedding = feature_tensor.cpu().numpy().flatten()
        
        # Normalizar el embedding para mejorar la comparación
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def extraer_multiples_embeddings(self, img: ImageArray, num_crops: int = 5) -> List[EmbeddingVector]:
        """
        Extrae múltiples embeddings de una imagen usando diferentes crops y augmentaciones
        para generar más variabilidad en los datos de entrenamiento
        
        Args:
            img: Imagen como array numpy
            num_crops: Número de crops diferentes a generar
            
        Returns:
            Lista de embeddings extraídos
        """
        if not DEPS_INSTALLED:
            raise ImportError("No se pueden extraer embeddings: faltan dependencias")
            
        embeddings = []
        h, w = img.shape[:2]
        
        # 1. Embedding de la imagen original
        embedding_original = self.extraer_embedding(img)
        embeddings.append(embedding_original)
        
        # 2. Generar crops aleatorios centrados en diferentes regiones
        for i in range(num_crops - 1):
            # Generar crop aleatorio pero manteniendo aspectos importantes
            crop_size = min(h, w) * (0.7 + 0.2 * np.random.random())  # Entre 70% y 90% del tamaño
            crop_size = int(crop_size)
            
            # Posición aleatoria pero no muy en los bordes
            margin_h = int(h * 0.1)
            margin_w = int(w * 0.1)
            
            max_y = max(0, h - crop_size - margin_h)
            max_x = max(0, w - crop_size - margin_w)
            
            if max_y > margin_h and max_x > margin_w:
                start_y = np.random.randint(margin_h, max_y)
                start_x = np.random.randint(margin_w, max_x)
                
                end_y = min(start_y + crop_size, h)
                end_x = min(start_x + crop_size, w)
                
                crop = img[start_y:end_y, start_x:end_x]
                
                # Solo usar el crop si es lo suficientemente grande
                if crop.shape[0] >= 64 and crop.shape[1] >= 64:
                    # Redimensionar el crop al tamaño esperado
                    crop_resized = cv2.resize(crop, (224, 224))
                    
                    # Aplicar augmentaciones sutiles
                    if np.random.random() > 0.5:  # 50% chance de flip horizontal
                        crop_resized = cv2.flip(crop_resized, 1)
                    
                    # Ligero ajuste de brillo (±10%)
                    brightness_factor = 0.9 + 0.2 * np.random.random()
                    crop_resized = np.clip(crop_resized * brightness_factor, 0, 255).astype(np.uint8)
                    
                    embedding_crop = self.extraer_embedding(crop_resized)
                    embeddings.append(embedding_crop)
        
        logger.info(f"Extraídos {len(embeddings)} embeddings de la imagen")
        return embeddings
    
    def crear_clasificador(self, tipo_modelo: str = 'knn', **kwargs) -> object:
        """
        Crea un nuevo clasificador del tipo especificado
        
        Args:
            tipo_modelo: Tipo de modelo ('knn', 'svm', 'rf')
            **kwargs: Parámetros adicionales para el clasificador
            
        Returns:
            Clasificador inicializado
        """
        if tipo_modelo == 'knn':
            # Parámetros más robustos para KNN
            n_neighbors = kwargs.get('n_neighbors', 7)  # Más vecinos para mayor estabilidad
            weights = kwargs.get('weights', 'distance')
            metric = kwargs.get('metric', 'cosine')  # Cosine distance funciona bien para embeddings
            algorithm = kwargs.get('algorithm', 'auto')
            return KNeighborsClassifier(
                n_neighbors=n_neighbors, 
                weights=weights, 
                metric=metric,
                algorithm=algorithm
            )
            
        elif tipo_modelo == 'svm':
            C = kwargs.get('C', 1.0)
            kernel = kwargs.get('kernel', 'rbf')
            probability = kwargs.get('probability', True)
            return SVC(C=C, kernel=kernel, probability=probability)
            
        elif tipo_modelo == 'rf':
            n_estimators = kwargs.get('n_estimators', 100)
            max_depth = kwargs.get('max_depth', None)
            return RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
            
        else:
            raise ValueError(f"Tipo de modelo no soportado: {tipo_modelo}")
    
    def entrenar_modelo(self, X: np.ndarray, y: np.ndarray, tipo_modelo: str = 'knn', **kwargs) -> Tuple[object, Dict]:
        """
        Entrena un modelo clasificador con los embeddings proporcionados
        
        Args:
            X: Matriz de embeddings (cada fila es un embedding)
            y: Vector de etiquetas (IDs de mascotas)
            tipo_modelo: Tipo de modelo a entrenar ('knn', 'svm', 'rf')
            **kwargs: Parámetros adicionales para el clasificador
            
        Returns:
            Tuple con (modelo entrenado, métricas de rendimiento)
        """
        # Crear y entrenar el clasificador
        start_time = time.time()
        clasificador = self.crear_clasificador(tipo_modelo, **kwargs)
        clasificador.fit(X, y)
        tiempo_entrenamiento = time.time() - start_time
        
        # Calcular métricas (si hay suficientes datos)
        metricas = {
            'tiempo_entrenamiento': tiempo_entrenamiento,
            'num_clases': len(np.unique(y)),
            'num_muestras': len(y)
        }
        
        # Si hay suficientes muestras, intentar hacer validación
        if len(y) > 20 and len(np.unique(y)) > 1:
            try:
                # Predicciones en el conjunto de entrenamiento (no ideal, pero informativo)
                y_pred = clasificador.predict(X)
                metricas['accuracy'] = accuracy_score(y, y_pred)
                metricas['precision'] = precision_score(y, y_pred, average='weighted', zero_division=0)
                metricas['recall'] = recall_score(y, y_pred, average='weighted', zero_division=0)
                metricas['f1'] = f1_score(y, y_pred, average='weighted', zero_division=0)
            except Exception as e:
                logger.warning(f"No se pudieron calcular métricas: {e}")
                
        return clasificador, metricas
    
    def guardar_modelo(self, modelo, ruta: Union[str, Path]):
        """Guarda un modelo entrenado en disco"""
        with open(ruta, 'wb') as f:
            pickle.dump(modelo, f)
            
    def cargar_modelo(self, ruta: Union[str, Path]):
        """Carga un modelo entrenado desde disco"""
        with open(ruta, 'rb') as f:
            return pickle.load(f)
            
    def predecir_con_multiples_embeddings(self, modelo, embedding_consulta: EmbeddingVector, embeddings_db: dict) -> Tuple[int, float]:
        """
        Predice usando múltiples embeddings por mascota para mayor precisión
        
        Args:
            modelo: Modelo clasificador entrenado  
            embedding_consulta: Embedding de la imagen a identificar
            embeddings_db: Dict {mascota_id: [lista_embeddings]} de embeddings reales de la BD
            
        Returns:
            Tuple con (ID de mascota predicha, confianza)
        """
        if embedding_consulta.ndim == 1:
            embedding_consulta = embedding_consulta.reshape(1, -1)
        
        # Calcular similitudes con todos los embeddings de cada mascota
        mejores_puntuaciones = {}
        
        for mascota_id, embeddings_mascota in embeddings_db.items():
            if not embeddings_mascota:
                continue
                
            # Calcular distancia coseno con cada embedding de esta mascota
            similitudes = []
            for emb in embeddings_mascota:
                emb_array = np.array(emb).reshape(1, -1)
                
                # Distancia coseno (1 - similitud coseno)
                dot_product = np.dot(embedding_consulta, emb_array.T)[0][0]
                norm_consulta = np.linalg.norm(embedding_consulta)
                norm_emb = np.linalg.norm(emb_array)
                
                if norm_consulta > 0 and norm_emb > 0:
                    similitud_coseno = dot_product / (norm_consulta * norm_emb)
                    similitudes.append(similitud_coseno)
            
            if similitudes:
                # Usar el PROMEDIO de las mejores similitudes (top 3 o todas si son menos)
                similitudes_ordenadas = sorted(similitudes, reverse=True)
                top_similitudes = similitudes_ordenadas[:min(3, len(similitudes_ordenadas))]
                similitud_promedio = np.mean(top_similitudes)
                
                # También considerar la consistencia (cuántos embeddings son similares)
                umbral_similitud = 0.7  # Umbral para considerar un embedding como "similar"
                embeddings_similares = sum(1 for sim in similitudes if sim >= umbral_similitud)
                factor_consistencia = embeddings_similares / len(similitudes)
                
                # Puntuación final combinando similitud y consistencia
                puntuacion = similitud_promedio * (0.8 + 0.2 * factor_consistencia)
                mejores_puntuaciones[mascota_id] = puntuacion
        
        if not mejores_puntuaciones:
            return -1, 0.0
        
        # Obtener la mejor puntuación
        mascota_predicha = max(mejores_puntuaciones, key=mejores_puntuaciones.get)
        mejor_similitud = mejores_puntuaciones[mascota_predicha]
        
        # Convertir similitud a confianza (0-1)
        # Solo alta confianza si la similitud es muy alta
        if mejor_similitud >= 0.85:  # Muy similar
            confianza = min(0.98, mejor_similitud + 0.1)
        elif mejor_similitud >= 0.75:  # Moderadamente similar
            confianza = mejor_similitud * 0.9
        else:  # Baja similitud
            confianza = mejor_similitud * 0.6
        
        # Verificar que haya una diferencia clara con la segunda mejor opción
        puntuaciones_ordenadas = sorted(mejores_puntuaciones.values(), reverse=True)
        if len(puntuaciones_ordenadas) > 1:
            diferencia = puntuaciones_ordenadas[0] - puntuaciones_ordenadas[1]
            if diferencia < 0.1:  # Si la diferencia es muy pequeña, reducir confianza
                confianza *= 0.7
        
        return mascota_predicha, float(np.clip(confianza, 0.0, 1.0))
    
    def predecir(self, modelo, embedding: EmbeddingVector) -> Tuple[int, float]:
        """
        Método de compatibilidad - usar predecir_con_multiples_embeddings cuando sea posible
        """
        # Predicción básica usando el modelo tradicional
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
            
        mascota_id = modelo.predict(embedding)[0]
        confianza = 0.3  # Confianza baja por defecto para método básico
        
        if hasattr(modelo, 'predict_proba'):
            probabilities = modelo.predict_proba(embedding)[0]
            confianza = probabilities[modelo.classes_.tolist().index(mascota_id)]
        elif hasattr(modelo, 'kneighbors'):
            distances, indices = modelo.kneighbors(embedding, n_neighbors=min(3, len(modelo._fit_X)))
            avg_distance = np.mean(distances[0])
            confianza = max(0.1, 1.0 - avg_distance)
            
        return mascota_id, float(np.clip(confianza, 0.0, 1.0))




def actualizar_modelo_global(tipo_modelo='knn', extractor='efficientnet_b0', **kwargs):
    """
    Actualiza el modelo global de reconocimiento entrenándolo con todos los embeddings disponibles
    
    Args:
        tipo_modelo: Tipo de clasificador ('knn', 'svm', 'rf')
        extractor: Modelo extractor de características ('efficientnet_b0', 'resnet50')
        **kwargs: Parámetros adicionales para el clasificador
        
    Returns:
        ModeloGlobal: Objeto del modelo actualizado
    """
    # Importamos aquí para evitar referencias circulares
    from ..models import ModeloGlobal, EmbeddingStore, Mascota
    
    # Verificar dependencias
    if not DEPS_INSTALLED:
        logger.error("No se puede actualizar el modelo: faltan dependencias")
        return None
        
    # Crear servicio de biometría
    servicio = BiometriaService(modelo_extractor=extractor)
    
    # Obtener TODOS los embeddings disponibles (tanto usados como no usados)
    # para entrenar un modelo completo con todas las mascotas
    embeddings = EmbeddingStore.objects.all()
    
    # Si no hay suficientes embeddings, salir
    if embeddings.count() < 5:
        logger.warning("No hay suficientes embeddings para entrenar el modelo global")
        return None
        
    # Debug: Log qué mascotas están siendo incluidas en el entrenamiento
    mascotas_en_entrenamiento = set()
    for emb in embeddings:
        mascotas_en_entrenamiento.add(emb.mascota.id)
    logger.info(f"Entrenando modelo con {len(mascotas_en_entrenamiento)} mascotas: {list(mascotas_en_entrenamiento)}")
    logger.info(f"Total embeddings para entrenamiento: {embeddings.count()}")
        
    # Preparar datos para entrenamiento
    X = []  # Matriz de embeddings
    y = []  # Vector de IDs de mascota
    
    for emb in embeddings:
        vector = np.array(emb.vector)
        X.append(vector)
        y.append(emb.mascota_id)
        
    X = np.array(X)
    y = np.array(y)
    
    # Entrenar el modelo
    clasificador, metricas = servicio.entrenar_modelo(X, y, tipo_modelo, **kwargs)
    
    # Guardar el modelo
    # Crear directorio para modelos si no existe
    ruta_modelos = os.path.join(settings.MEDIA_ROOT, 'modelos')
    os.makedirs(ruta_modelos, exist_ok=True)
    
    # Generar nombre único para el archivo
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"modelo_global_{tipo_modelo}_{timestamp}.pkl"
    ruta_archivo = os.path.join(ruta_modelos, nombre_archivo)
    
    # Guardar el modelo
    servicio.guardar_modelo(clasificador, ruta_archivo)
    
    # Crear nuevo registro de ModeloGlobal
    ultimo_modelo = ModeloGlobal.objects.order_by('-version').first()
    version = 1
    if ultimo_modelo:
        version = ultimo_modelo.version + 1
        
    # Cargar el archivo para el FileField
    with open(ruta_archivo, 'rb') as f:
        contenido_modelo = f.read()
    
    # Desactivar modelos anteriores
    ModeloGlobal.objects.filter(activo=True).update(activo=False)
    
    # Crear objeto ModeloGlobal
    modelo_global = ModeloGlobal.objects.create(
        nombre=f"modelo_global_{timestamp}",
        tipo_modelo=tipo_modelo,
        extractor_caracteristicas=extractor,
        version=version,
        hiperparametros=kwargs,
        metricas=metricas,
        num_clases=metricas.get('num_clases', 0),
        num_imagenes_entrenamiento=metricas.get('num_muestras', 0),
        tiempo_entrenamiento=metricas.get('tiempo_entrenamiento', 0),
        activo=True
    )
    
    # Asignar archivo al FileField
    modelo_global.modelo_file.save(nombre_archivo, ContentFile(contenido_modelo))
    
    # Marcar embeddings como usados en entrenamiento
    embeddings.update(usado_en_entrenamiento=True)
    
    # Actualizar estado de mascotas
    for mascota_id in np.unique(y):
        mascota = Mascota.objects.get(id=mascota_id)
        mascota.biometria_entrenada = True
        mascota.save()
        
    logger.info(f"Modelo global actualizado: v{version} ({tipo_modelo}) - {metricas.get('num_clases', 0)} mascotas")
    
    return modelo_global


def procesar_imagen_mascota(imagen_mascota_id):
    """
    Procesa una imagen de mascota para extraer múltiples embeddings
    
    Args:
        imagen_mascota_id: ID de ImagenMascota a procesar
        
    Returns:
        List[EmbeddingStore]: Lista de objetos de embedding creados
    """
    # Importamos aquí para evitar referencias circulares
    from ..models import ImagenMascota, EmbeddingStore
    
    # Verificar dependencias
    if not DEPS_INSTALLED:
        logger.error("No se puede procesar imagen: faltan dependencias")
        return None
        
    # Obtener la imagen
    imagen = ImagenMascota.objects.get(id=imagen_mascota_id)
    
    # Si no es biométrica o ya está procesada, salir
    if not imagen.is_biometrica or imagen.procesada:
        logger.info(f"Imagen {imagen_mascota_id} no requiere procesamiento")
        return None
        
    # Crear servicio
    servicio = BiometriaService()
    
    # Procesar imagen
    try:
        # Cargar y preprocesar imagen
        img = servicio.procesar_imagen(imagen.imagen.path)
        
        # Detectar mascota en la imagen
        img_recortada, coords = servicio.detectar_mascota(img)
        
        # Validar que la imagen recortada sea de calidad suficiente
        if img_recortada.shape[0] < 64 or img_recortada.shape[1] < 64:
            logger.warning(f"Imagen {imagen_mascota_id} demasiado pequeña después del recorte")
            img_recortada = img  # Usar imagen original si el recorte es muy pequeño
        
        # Extraer múltiples embeddings para mayor robustez
        embeddings = servicio.extraer_multiples_embeddings(img_recortada, num_crops=4)
        
        # Guardar todos los embeddings
        embedding_stores = []
        for i, embedding in enumerate(embeddings):
            embedding_store = EmbeddingStore.objects.create(
                mascota=imagen.mascota,
                imagen=imagen,
                vector=embedding.tolist(),  # Convertir a lista para JSONField
                dimension=len(embedding),
                modelo_extractor=servicio.modelo_extractor,
                crop_index=i  # Índice del crop para identificación
            )
            embedding_stores.append(embedding_store)
        
        # Marcar imagen como procesada
        imagen.procesada = True
        imagen.calidad = 0.9 if len(embeddings) >= 3 else 0.7  # Calidad basada en número de embeddings
        imagen.save()
        
        logger.info(f"Extraídos {len(embeddings)} embeddings para imagen {imagen_mascota_id}")
        return embedding_stores
        
    except Exception as e:
        logger.error(f"Error procesando imagen {imagen_mascota_id}: {e}")
        return None


def reconocer_mascota(ruta_imagen, usuario=None):
    """
    Reconoce una mascota a partir de una imagen
    
    Args:
        ruta_imagen: Ruta a la imagen a analizar
        usuario: Usuario que realiza el reconocimiento (opcional)
        
    Returns:
        dict: Información del reconocimiento (mascota_id, confianza, etc.)
    """
    # Importamos aquí para evitar referencias circulares
    from ..models import ModeloGlobal, Mascota, RegistroReconocimiento
    import os
    from django.core.files import File
    
    # Verificar dependencias
    if not DEPS_INSTALLED:
        return {"error": "No se pueden hacer reconocimientos: faltan dependencias"}
    
    # Obtener modelo activo
    modelo_global = ModeloGlobal.get_active_model()
    if not modelo_global or not modelo_global.modelo_file:
        return {"error": "No hay modelo global activo"}
        
    # Crear servicio con el extractor correcto
    servicio = BiometriaService(modelo_extractor=modelo_global.extractor_caracteristicas)
    
    # Medir tiempo de procesamiento
    inicio = time.time()
    
    try:
        # Cargar modelo
        clasificador = servicio.cargar_modelo(modelo_global.modelo_file.path)
        
        # Procesar imagen
        img = servicio.procesar_imagen(ruta_imagen)
        img_recortada, coords = servicio.detectar_mascota(img)
        
        # Verificar que se detectó correctamente una cara de mascota
        if img_recortada is None or img_recortada.size == 0:
            return {"error": "No se detectó una mascota válida en la imagen"}
            
        # Verificar tamaño mínimo de la región detectada
        if img_recortada.shape[0] < 50 or img_recortada.shape[1] < 50:
            return {"error": "La región detectada es demasiado pequeña para ser una mascota"}
            
        # Obtener TODOS los embeddings reales de la base de datos
        from ..models import EmbeddingStore
        embeddings_db = {}
        
        # Agrupar embeddings por mascota_id
        todos_los_embeddings = EmbeddingStore.objects.select_related('mascota').all()
        for emb_store in todos_los_embeddings:
            mascota_id = emb_store.mascota_id
            if mascota_id not in embeddings_db:
                embeddings_db[mascota_id] = []
            embeddings_db[mascota_id].append(emb_store.vector)
        
        logger.info(f"Cargados embeddings de {len(embeddings_db)} mascotas para predicción")
        for mid, embs in embeddings_db.items():
            logger.info(f"Mascota {mid}: {len(embs)} embeddings")
        
        # Extraer embedding de la imagen a identificar
        embedding_consulta = servicio.extraer_embedding(img_recortada)
        
        # Usar predicción con múltiples embeddings si hay datos suficientes
        if embeddings_db and len(embeddings_db) > 0:
            mascota_id, confianza = servicio.predecir_con_multiples_embeddings(
                clasificador, embedding_consulta, embeddings_db
            )
        else:
            # Fallback al método tradicional si no hay embeddings en BD
            mascota_id, confianza = servicio.predecir(clasificador, embedding_consulta)
        
        # Tiempo total
        tiempo_total = time.time() - inicio
        
        # Crear registro
        registro = RegistroReconocimiento(
            confianza=confianza,
            tiempo_procesamiento=tiempo_total,
            usuario=usuario if usuario else None
        )
        
        # Umbral de confianza del 30% (modificado desde 70%)
        umbral_confianza = 0.30  # 30% o más
        exito = confianza >= umbral_confianza
        
        # Log para debugging
        logger.info(f"Reconocimiento - Mascota ID: {mascota_id}, Confianza: {confianza:.3f}, Éxito: {exito}")
        
        if exito:
            try:
                mascota = Mascota.objects.get(id=mascota_id)
                registro.mascota_predicha = mascota
                registro.exito = True
            except Mascota.DoesNotExist:
                exito = False
        
        # Guardar la imagen analizada en el registro
        with open(ruta_imagen, 'rb') as f:
            registro.imagen_analizada.save(
                os.path.basename(ruta_imagen),
                File(f)
            )
        
        # Guardar detalles
        registro.detalles = {
            'tiempo': tiempo_total,
            'confianza': confianza,
            'umbral_aplicado': umbral_confianza,
            'tipo_modelo': modelo_global.tipo_modelo,
            'modelo_version': modelo_global.version
        }
        
        # Guardar registro
        registro.save()
        
        # Generar mensaje personalizado según la confianza
        if exito:
            mensaje = f"¡Mascota identificada exitosamente! Confianza: {confianza:.1%}"
        else:
            if confianza >= 0.25:
                mensaje = f"No se puede identificar la mascota. Confianza del {confianza:.1%} (se requiere 30% o más para una identificación segura)."
            elif confianza >= 0.15:
                mensaje = f"No se puede identificar la mascota. Confianza insuficiente: {confianza:.1%} (se requiere 30% o más)."
            elif confianza >= 0.10:
                mensaje = f"No se puede identificar la mascota. La imagen puede ser de una mascota no registrada o la calidad es insuficiente ({confianza:.1%})."
            else:
                mensaje = f"No se puede identificar la mascota. Esta imagen no corresponde a ninguna mascota registrada en el sistema ({confianza:.1%})."
        
        # Retornar resultado
        resultado = {
            "exito": exito,
            "mascota_id": int(mascota_id) if exito else None,
            "confianza": float(confianza),
            "tiempo_procesamiento": float(tiempo_total),
            "registro_id": registro.id,
            "mensaje": mensaje,
            "umbral_requerido": umbral_confianza
        }
        
        if exito:
            # Añadir información completa de la mascota si fue exitoso
            mascota = Mascota.objects.get(id=mascota_id)
            
            # Información completa de la mascota
            resultado["mascota"] = {
                "id": mascota.id,
                "nombre": mascota.nombre,
                "raza": mascota.raza or "Sin raza específica",
                "edad": mascota.edad,
                "peso": float(mascota.peso) if mascota.peso else None,
                "color": mascota.color,
                "genero": mascota.sexo,  # El campo correcto es 'sexo'
                "fecha_nacimiento": mascota.fecha_nacimiento.strftime('%d/%m/%Y') if mascota.fecha_nacimiento else None,
                "fecha_registro": mascota.created_at.strftime('%d/%m/%Y') if mascota.created_at else None,
                "foto_perfil": mascota.foto_perfil.url if mascota.foto_perfil else None,
                "url_detalle": mascota.get_absolute_url(),
                "caracteristicas_especiales": mascota.caracteristicas_especiales,
                "estado_salud": mascota.estado_corporal or 'Normal',  # El campo correcto es 'estado_corporal'
                "etapa_vida": mascota.etapa_vida,
                "biometria_entrenada": mascota.biometria_entrenada,
                "confianza_biometrica": mascota.confianza_biometrica
            }
            
            # Información completa del propietario
            if mascota.propietario:
                propietario = mascota.propietario
                resultado["propietario"] = {
                    "id": propietario.id,
                    "username": propietario.username,
                    "nombre_completo": f"{propietario.first_name} {propietario.last_name}".strip() or propietario.username,
                    "email": propietario.email,
                    "telefono": propietario.phone,  
                    "direccion": propietario.direction,  # El campo correcto es 'direction'
                    "dni": propietario.dni,
                    "fecha_registro": propietario.date_joined.strftime('%d/%m/%Y') if propietario.date_joined else None,
                    "foto_perfil": propietario.image.url if propietario.image else None,  # El campo correcto es 'image'
                    "rol": propietario.role if hasattr(propietario, 'role') else 'OWNER'
                }
            else:
                resultado["propietario"] = None
            
        return resultado
        
    except Exception as e:
        logger.error(f"Error en reconocimiento: {e}")
        return {"error": str(e)}