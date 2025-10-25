"""
Sistema de reconocimiento facial usando OpenCV y el modelo YuNet
Detecta rostros y genera descriptores para autenticación biométrica
"""
import cv2
import numpy as np
import json
import base64
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FacialRecognitionSystem:
    """Sistema de reconocimiento facial para autenticación de usuarios"""
    
    # Ruta al modelo ONNX de detección facial
    MODEL_PATH = Path(settings.BASE_DIR) / 'models' / 'face_detection_yunet_2023mar_int8.onnx'
    
    # Parámetros de configuración
    CONFIDENCE_THRESHOLD = 0.7  # Umbral de confianza para detección
    NMS_THRESHOLD = 0.3  # Non-maximum suppression
    TOP_K = 5000  # Máximo de detecciones antes de NMS
    
    # Parámetros para comparación de rostros
    SIMILARITY_THRESHOLD = 0.65  # Umbral para considerar rostros similares
    
    def __init__(self):
        """Inicializa el detector de rostros con YuNet"""
        try:
            # Cargar el modelo YuNet
            self.detector = cv2.FaceDetectorYN.create(
                str(self.MODEL_PATH),
                "",
                (320, 320),
                self.CONFIDENCE_THRESHOLD,
                self.NMS_THRESHOLD,
                self.TOP_K
            )
            logger.info("Detector facial YuNet inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar detector facial: {e}")
            raise
    
    def preprocess_image(self, image_data):
        """
        Preprocesa la imagen para detección
        
        Args:
            image_data: bytes o array numpy con la imagen
            
        Returns:
            numpy.ndarray: Imagen preprocesada
        """
        if isinstance(image_data, bytes):
            # Convertir bytes a numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = image_data
        
        if image is None:
            raise ValueError("No se pudo cargar la imagen")
        
        # Convertir a RGB si es necesario
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        return image
    
    def detect_faces(self, image_data):
        """
        Detecta rostros en la imagen
        
        Args:
            image_data: bytes o numpy array con la imagen
            
        Returns:
            tuple: (imagen_procesada, lista_de_rostros, confianza)
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
            
            # Obtener el rostro con mayor confianza
            best_face = faces[0]
            confidence = float(best_face[-1])
            
            # Extraer coordenadas del bounding box
            x, y, w, h = best_face[:4].astype(int)
            
            # Extraer landmarks (5 puntos faciales)
            landmarks = best_face[4:14].reshape(5, 2).astype(int)
            
            face_info = {
                'bbox': [int(x), int(y), int(w), int(h)],
                'landmarks': landmarks.tolist(),
                'confidence': confidence
            }
            
            return image, [face_info], confidence
            
        except Exception as e:
            logger.error(f"Error en detección de rostros: {e}")
            return None, [], 0.0
    
    def extract_face_descriptor(self, image_data):
        """
        Extrae un descriptor facial de la imagen
        
        Args:
            image_data: bytes o numpy array con la imagen
            
        Returns:
            dict: Diccionario con el descriptor y metadatos
        """
        try:
            image, faces, confidence = self.detect_faces(image_data)
            
            if not faces or confidence < self.CONFIDENCE_THRESHOLD:
                return None
            
            face_info = faces[0]
            x, y, w, h = face_info['bbox']
            
            # Extraer región del rostro con margen
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(image.shape[1], x + w + margin)
            y2 = min(image.shape[0], y + h + margin)
            
            face_roi = image[y1:y2, x1:x2]
            
            # Redimensionar a tamaño estándar
            face_roi = cv2.resize(face_roi, (128, 128))
            
            # Generar descriptor basado en múltiples características
            descriptor = self._generate_descriptor(face_roi, face_info['landmarks'])
            
            return {
                'descriptor': descriptor,
                'bbox': face_info['bbox'],
                'confidence': confidence,
                'landmarks': face_info['landmarks']
            }
            
        except Exception as e:
            logger.error(f"Error al extraer descriptor facial: {e}")
            return None
    
    def _generate_descriptor(self, face_roi, landmarks):
        """
        Genera un descriptor robusto combinando múltiples características
        
        Args:
            face_roi: Región del rostro normalizada
            landmarks: Puntos de referencia faciales
            
        Returns:
            list: Descriptor facial normalizado
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # 1. Histograma de LBP (Local Binary Patterns)
        lbp = self._compute_lbp(gray)
        hist_lbp = cv2.calcHist([lbp], [0], None, [256], [0, 256])
        hist_lbp = hist_lbp.flatten() / (hist_lbp.sum() + 1e-7)
        
        # 2. Histograma de gradientes orientados (HOG simplificado)
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag, ang = cv2.cartToPolar(gx, gy)
        hist_hog = cv2.calcHist([ang], [0], None, [18], [0, 2*np.pi])
        hist_hog = hist_hog.flatten() / (hist_hog.sum() + 1e-7)
        
        # 3. Características de textura (Gabor simplificado con diferentes escalas)
        gabor_features = []
        for theta in [0, np.pi/4, np.pi/2, 3*np.pi/4]:
            kernel = cv2.getGaborKernel((21, 21), 5, theta, 10, 0.5, 0)
            filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
            gabor_features.extend([filtered.mean(), filtered.std()])
        gabor_features = np.array(gabor_features)
        gabor_features = gabor_features / (np.linalg.norm(gabor_features) + 1e-7)
        
        # 4. Características geométricas de landmarks
        if landmarks and len(landmarks) >= 5:
            landmarks_arr = np.array(landmarks, dtype=np.float32)
            # Normalizar landmarks relativos al centro
            center = landmarks_arr.mean(axis=0)
            landmarks_norm = (landmarks_arr - center) / (np.linalg.norm(landmarks_arr - center) + 1e-7)
            geometric_features = landmarks_norm.flatten()
        else:
            geometric_features = np.zeros(10)
        
        # Combinar todas las características
        descriptor = np.concatenate([
            hist_lbp[:64],  # 64 bins del LBP
            hist_hog,       # 18 bins del HOG
            gabor_features, # 8 características Gabor
            geometric_features  # 10 características geométricas
        ])
        
        # Normalizar descriptor final
        descriptor = descriptor / (np.linalg.norm(descriptor) + 1e-7)
        
        return descriptor.tolist()
    
    def _compute_lbp(self, gray_image):
        """
        Calcula Local Binary Pattern
        
        Args:
            gray_image: Imagen en escala de grises
            
        Returns:
            numpy.ndarray: Imagen con patrones LBP
        """
        h, w = gray_image.shape
        lbp = np.zeros_like(gray_image)
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                center = gray_image[i, j]
                code = 0
                code |= (gray_image[i-1, j-1] >= center) << 7
                code |= (gray_image[i-1, j] >= center) << 6
                code |= (gray_image[i-1, j+1] >= center) << 5
                code |= (gray_image[i, j+1] >= center) << 4
                code |= (gray_image[i+1, j+1] >= center) << 3
                code |= (gray_image[i+1, j] >= center) << 2
                code |= (gray_image[i+1, j-1] >= center) << 1
                code |= (gray_image[i, j-1] >= center) << 0
                lbp[i, j] = code
        
        return lbp
    
    def compare_faces(self, descriptor1, descriptor2):
        """
        Compara dos descriptores faciales
        
        Args:
            descriptor1: Primer descriptor (dict o list)
            descriptor2: Segundo descriptor (dict o list)
            
        Returns:
            tuple: (similaridad, es_coincidencia)
        """
        try:
            # Extraer descriptores si vienen en formato dict
            if isinstance(descriptor1, dict):
                desc1 = np.array(descriptor1.get('descriptor', descriptor1))
            else:
                desc1 = np.array(descriptor1)
            
            if isinstance(descriptor2, dict):
                desc2 = np.array(descriptor2.get('descriptor', descriptor2))
            else:
                desc2 = np.array(descriptor2)
            
            # Calcular similitud coseno
            similarity = np.dot(desc1, desc2) / (
                np.linalg.norm(desc1) * np.linalg.norm(desc2) + 1e-7
            )
            
            is_match = similarity >= self.SIMILARITY_THRESHOLD
            
            return float(similarity), is_match
            
        except Exception as e:
            logger.error(f"Error al comparar rostros: {e}")
            return 0.0, False
    
    def draw_face_box(self, image, face_info, is_match=False, similarity=0.0):
        """
        Dibuja un cuadro alrededor del rostro detectado
        
        Args:
            image: Imagen donde dibujar
            face_info: Información del rostro
            is_match: Si hubo coincidencia
            similarity: Puntuación de similitud
            
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
        
        # Agregar texto con la confianza
        text = f"Conf: {face_info['confidence']:.2f}"
        if similarity > 0:
            text += f" | Sim: {similarity:.2f}"
        
        cv2.putText(image, text, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def serialize_descriptor(self, descriptor_data):
        """
        Serializa el descriptor para almacenar en base de datos
        
        Args:
            descriptor_data: Diccionario con descriptor y metadatos
            
        Returns:
            str: JSON string del descriptor
        """
        return json.dumps(descriptor_data)
    
    def deserialize_descriptor(self, descriptor_json):
        """
        Deserializa el descriptor desde la base de datos
        
        Args:
            descriptor_json: JSON string del descriptor
            
        Returns:
            dict: Diccionario con descriptor y metadatos
        """
        return json.loads(descriptor_json)


# Instancia global del sistema de reconocimiento
facial_system = FacialRecognitionSystem()
