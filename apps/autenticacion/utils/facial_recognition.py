"""
Sistema de reconocimiento facial usando ArcFace + YuNet
- YuNet: Detección de rostros y landmarks
- ArcFace: Extracción de embeddings de 512 dimensiones para autenticación biométrica
"""
import cv2
import numpy as np
import json
import base64
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ArcFaceSystem:
    """Sistema de reconocimiento facial con ArcFace ResNet100 + YuNet detector"""
    
    # Rutas a los modelos ONNX
    YUNET_MODEL_PATH = Path(settings.BASE_DIR) / 'models' / 'face_detection_yunet_2023mar_int8.onnx'
    ARCFACE_MODEL_PATH = Path(settings.BASE_DIR) / 'models' / 'arcfaceresnet100-8.onnx'
    
    # Configuración YuNet (Detección)
    YUNET_CONFIDENCE_THRESHOLD = 0.7  # Umbral de confianza para detección
    YUNET_NMS_THRESHOLD = 0.3  # Non-maximum suppression
    YUNET_TOP_K = 5000  # Máximo de detecciones antes de NMS
    
    # Configuración ArcFace (Reconocimiento)
    ARCFACE_SIMILARITY_THRESHOLD = 0.40  # Threshold recomendado para ArcFace (doc oficial)
    ARCFACE_INPUT_SIZE = (112, 112)  # Tamaño de entrada requerido por ArcFace
    EMBEDDING_SIZE = 512  # Dimensiones del vector de salida
    CONFIDENCE_THRESHOLD = 0.7  # Confianza mínima para aceptar registro
    
    def __init__(self):
        """Inicializa YuNet (detector) y ArcFace (recognizer)"""
        try:
            # Verificar que existan los modelos
            if not self.YUNET_MODEL_PATH.exists():
                raise FileNotFoundError(f"Modelo YuNet no encontrado: {self.YUNET_MODEL_PATH}")
            if not self.ARCFACE_MODEL_PATH.exists():
                raise FileNotFoundError(f"Modelo ArcFace no encontrado: {self.ARCFACE_MODEL_PATH}")
            
            # Cargar YuNet para detección de rostros
            self.detector = cv2.FaceDetectorYN.create(
                str(self.YUNET_MODEL_PATH),
                "",
                (320, 320),  # Tamaño inicial, se ajustará dinámicamente
                self.YUNET_CONFIDENCE_THRESHOLD,
                self.YUNET_NMS_THRESHOLD,
                self.YUNET_TOP_K
            )
            
            # Cargar ArcFace para reconocimiento facial
            self.recognizer = cv2.FaceRecognizerSF.create(
                str(self.ARCFACE_MODEL_PATH),
                ""
            )
            
            logger.info("✓ YuNet detector inicializado correctamente")
            logger.info("✓ ArcFace recognizer inicializado correctamente")
            
        except Exception as e:
            logger.error(f"✗ Error al inicializar sistema de reconocimiento facial: {e}")
            raise
    
    def preprocess_image(self, image_data):
        """
        Preprocesa la imagen para detección
        
        Args:
            image_data: bytes o array numpy con la imagen
            
        Returns:
            numpy.ndarray: Imagen preprocesada en formato BGR
        """
        if isinstance(image_data, bytes):
            # Convertir bytes a numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = image_data
        
        if image is None:
            raise ValueError("No se pudo cargar la imagen")
        
        # Convertir a BGR si es necesario (YuNet espera BGR)
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        return image
    
    def detect_faces(self, image_data):
        """
        Detecta rostros en la imagen usando YuNet
        
        Args:
            image_data: bytes o numpy array con la imagen
            
        Returns:
            tuple: (imagen_procesada, lista_de_rostros, confianza_max)
        """
        try:
            image = self.preprocess_image(image_data)
            h, w = image.shape[:2]
            
            # Actualizar el tamaño de entrada del detector
            self.detector.setInputSize((w, h))
            
            # Detectar rostros
            _, faces = self.detector.detect(image)
            
            if faces is None or len(faces) == 0:
                return image, [], 0.0
            
            # Procesar todos los rostros detectados
            face_list = []
            for face in faces:
                confidence = float(face[-1])
                x, y, w_face, h_face = face[:4].astype(int)
                landmarks = face[4:14].reshape(5, 2).astype(int)
                
                face_info = {
                    'bbox': [int(x), int(y), int(w_face), int(h_face)],
                    'landmarks': landmarks.tolist(),
                    'confidence': confidence
                }
                face_list.append(face_info)
            
            # Ordenar por confianza descendente
            face_list.sort(key=lambda f: f['confidence'], reverse=True)
            max_confidence = face_list[0]['confidence'] if face_list else 0.0
            
            return image, face_list, max_confidence
            
        except Exception as e:
            logger.error(f"Error en detección de rostros: {e}")
            return None, [], 0.0
    
    def detect_and_validate_single_face(self, image_data):
        """
        Detecta rostros y VALIDA que haya exactamente UNO
        
        Args:
            image_data: bytes o numpy array con la imagen
            
        Returns:
            tuple: (imagen, face_info, error_message)
                - Si todo OK: (image, face_info, None)
                - Si error: (None, None, mensaje_de_error)
        """
        try:
            image, faces, _ = self.detect_faces(image_data)
            
            # Validación 1: Sin rostros
            if not faces or len(faces) == 0:
                return None, None, "No se detectó ningún rostro. Asegúrate de estar frente a la cámara con buena iluminación."
            
            # Validación 2: Múltiples rostros (CRÍTICA)
            if len(faces) > 1:
                return None, None, f"Se detectaron {len(faces)} rostros. Solo debe haber UNA persona frente a la cámara."
            
            # Validación 3: Confianza mínima
            face = faces[0]
            if face['confidence'] < self.YUNET_CONFIDENCE_THRESHOLD:
                return None, None, f"La calidad del rostro es baja ({face['confidence']:.1%}). Mejora la iluminación o acércate a la cámara."
            
            return image, face, None
            
        except Exception as e:
            logger.error(f"Error en validación de rostro: {e}")
            return None, None, f"Error al procesar imagen: {str(e)}"
    
    def extract_face_embedding(self, image_data):
        """
        Extrae embedding de 512 dimensiones usando ArcFace
        
        Proceso:
        1. Detecta y valida que haya UN solo rostro
        2. Alinea el rostro usando landmarks de YuNet
        3. Extrae embedding con ArcFace (512 dims)
        4. Normaliza a longitud unitaria
        
        Args:
            image_data: bytes o numpy array con la imagen
            
        Returns:
            tuple: (embedding_dict, error_message)
                - Si OK: ({'embedding': [...], 'confidence': 0.95, ...}, None)
                - Si error: (None, mensaje_de_error)
        """
        try:
            # 1. Detectar y validar un solo rostro
            image, face_info, error = self.detect_and_validate_single_face(image_data)
            
            if error:
                return None, error
            
            # 2. Preparar datos del rostro para alineación
            # YuNet devuelve: [x, y, w, h, ...landmarks...]
            face_data = np.array(
                face_info['bbox'] + [coord for landmark in face_info['landmarks'] for coord in landmark],
                dtype=np.float32
            )
            
            # 3. Alinear rostro a 112x112 (requerido por ArcFace)
            aligned_face = self.recognizer.alignCrop(image, face_data)
            
            # 4. Extraer embedding con ArcFace
            embedding = self.recognizer.feature(aligned_face)
            
            # 5. Normalizar a longitud unitaria (para similitud coseno)
            embedding_norm = embedding / (np.linalg.norm(embedding) + 1e-7)
            
            # 6. Preparar resultado
            result = {
                'embedding': embedding_norm.flatten().tolist(),
                'confidence': face_info['confidence'],
                'bbox': face_info['bbox'],
                'landmarks': face_info['landmarks'],
                'embedding_size': len(embedding_norm.flatten()),
                'model_version': 'arcfaceresnet100-8'
            }
            
            logger.info(f"✓ Embedding extraído: {result['embedding_size']} dims, confianza: {result['confidence']:.2%}")
            
            return result, None
            
        except Exception as e:
            logger.error(f"✗ Error al extraer embedding facial: {e}")
            return None, f"Error al procesar rostro: {str(e)}"
    
    def compare_embeddings(self, embedding1, embedding2):
        """
        Compara dos embeddings de ArcFace usando similitud coseno
        
        Args:
            embedding1: dict o list con el primer embedding
            embedding2: dict o list con el segundo embedding
            
        Returns:
            tuple: (similarity_score, is_match)
                - similarity_score: float (0.0 - 1.0)
                - is_match: bool (True si >= threshold)
        """
        try:
            # Extraer embeddings si vienen en formato dict
            if isinstance(embedding1, dict):
                emb1 = np.array(embedding1.get('embedding', embedding1))
            else:
                emb1 = np.array(embedding1)
            
            if isinstance(embedding2, dict):
                emb2 = np.array(embedding2.get('embedding', embedding2))
            else:
                emb2 = np.array(embedding2)
            
            # Validar dimensiones
            if len(emb1) != self.EMBEDDING_SIZE or len(emb2) != self.EMBEDDING_SIZE:
                logger.warning(f"Dimensiones incorrectas: {len(emb1)} vs {len(emb2)}, esperado: {self.EMBEDDING_SIZE}")
                return 0.0, False
            
            # Similitud coseno (ya están normalizados)
            similarity = float(np.dot(emb1, emb2))
            
            # Aplicar threshold de ArcFace
            is_match = similarity >= self.ARCFACE_SIMILARITY_THRESHOLD
            
            return similarity, is_match
            
        except Exception as e:
            logger.error(f"Error al comparar embeddings: {e}")
            return 0.0, False
            logger.error(f"Error al comparar embeddings: {e}")
            return 0.0, False
    
    def draw_face_box(self, image, face_info, is_match=False, similarity=0.0):
        """
        Dibuja un cuadro alrededor del rostro detectado
        
        Args:
            image: Imagen donde dibujar
            face_info: Información del rostro (dict con bbox, landmarks, confidence)
            is_match: Si hubo coincidencia en reconocimiento
            similarity: Puntuación de similitud (0.0 - 1.0)
            
        Returns:
            numpy.ndarray: Imagen con el cuadro dibujado
        """
        x, y, w, h = face_info['bbox']
        
        # Color verde si es coincidencia, azul si no
        color = (0, 255, 0) if is_match else (255, 0, 0)
        
        # Dibujar rectángulo
        cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
        
        # Dibujar landmarks si están disponibles
        if 'landmarks' in face_info:
            for point in face_info['landmarks']:
                cv2.circle(image, tuple(point), 2, color, -1)
        
        # Agregar texto con la confianza y similitud
        text = f"Det: {face_info['confidence']:.2f}"
        if similarity > 0:
            text += f" | Sim: {similarity:.2f}"
        
        cv2.putText(image, text, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def serialize_embedding(self, embedding_data):
        """
        Serializa el embedding para almacenar en base de datos
        
        Args:
            embedding_data: Diccionario con embedding y metadatos
            
        Returns:
            str: JSON string del embedding
        """
        return json.dumps(embedding_data)
    
    def deserialize_embedding(self, embedding_json):
        """
        Deserializa el embedding desde la base de datos
        
        Args:
            embedding_json: JSON string del embedding
            
        Returns:
            dict: Diccionario con embedding y metadatos
        """
        return json.loads(embedding_json)


# Instancia global del sistema de reconocimiento facial con ArcFace
arcface_system = ArcFaceSystem()
