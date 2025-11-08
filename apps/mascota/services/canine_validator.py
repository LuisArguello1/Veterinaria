# apps/mascota/services/canine_validator.py
"""
Validador de imágenes caninas usando ImageNet.
Detecta si una imagen contiene un perro de cualquier raza usando modelos pre-entrenados.
"""

import logging
from typing import Dict, Union, Any
from io import BytesIO

logger = logging.getLogger(__name__)

# Importaciones condicionales
try:
    import torch
    import numpy as np
    from PIL import Image
    from torchvision import models, transforms
    DEPS_INSTALLED = True
except ImportError:
    DEPS_INSTALLED = False
    logger.warning("Dependencias de validación canina no instaladas. Instala: torch, torchvision, Pillow")


class CanineValidator:
    """
    Validador de imágenes caninas usando ImageNet.
    Usa MobileNetV2 pre-entrenado para detectar si una imagen contiene un perro.
    """
    
    # Rango de clases de perros en ImageNet (151-268 = 118 razas)
    DOG_CLASSES_RANGE = (151, 268)
    
    # Umbral mínimo de confianza para considerar válida la detección
    MIN_CONFIDENCE = 15.0  # 15% - Más permisivo para capturar más casos
    
    # Número de predicciones top a evaluar
    TOP_K = 5  # Evaluar las 5 predicciones más probables
    
    def __init__(self):
        """Inicializa el validador con el modelo ImageNet."""
        if not DEPS_INSTALLED:
            logger.error("No se puede inicializar validador: faltan dependencias")
            self.model = None
            return
        
        try:
            # Usar MobileNetV2 por ser ligero (~14 MB) y rápido
            logger.info("Cargando modelo MobileNetV2 para validación canina...")
            
            # Usar weights en lugar de pretrained (deprecación resuelta)
            from torchvision.models import MobileNet_V2_Weights
            weights = MobileNet_V2_Weights.IMAGENET1K_V1
            self.model = models.mobilenet_v2(weights=weights)
            self.model.eval()  # Modo evaluación
            
            # Transformaciones mejoradas de ImageNet
            # Usar múltiples crops para mejor detección
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            # Transformación alternativa sin crop (para imágenes ya cuadradas)
            self.transform_no_crop = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            logger.info("Modelo de validación canina cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al cargar modelo de validación: {e}")
            self.model = None
    
    def validar_imagen(self, imagen_input: Union[bytes, str, Any]) -> Dict:
        """
        Valida que la imagen contenga un canino.
        
        Args:
            imagen_input: Puede ser:
                - bytes: Imagen en formato bytes
                - str: Path al archivo de imagen
                - PIL.Image: Objeto de imagen PIL
                - Django UploadedFile: Archivo subido
                
        Returns:
            dict: {
                'es_canino': bool - Si la imagen contiene un perro
                'confianza': float - Confianza de la predicción (0-100)
                'clase_id': int - ID de clase ImageNet detectada
                'objeto_detectado': str - Nombre del objeto detectado
                'mensaje': str - Mensaje descriptivo del resultado
            }
        """
        if not DEPS_INSTALLED or self.model is None:
            # Si no hay dependencias, asumir válido (modo degradado)
            logger.warning("Validación canina deshabilitada - faltan dependencias")
            return {
                'es_canino': True,
                'confianza': 100.0,
                'clase_id': None,
                'objeto_detectado': 'Validación deshabilitada',
                'mensaje': 'Sistema de validación no disponible - imagen aceptada por defecto'
            }
        
        try:
            # Cargar imagen según el tipo de input
            img = self._cargar_imagen(imagen_input)
            
            if img is None:
                return {
                    'es_canino': False,
                    'confianza': 0.0,
                    'clase_id': None,
                    'objeto_detectado': 'Error',
                    'mensaje': 'No se pudo cargar la imagen'
                }
            
            # Transformar imagen y hacer predicción
            img_tensor = self.transform(img).unsqueeze(0)
            
            with torch.no_grad():
                output = self.model(img_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
            # Obtener top-K predicciones (evaluar las 5 más probables)
            top_probs, top_classes = probabilities.topk(self.TOP_K)
            
            # Convertir a listas de Python
            top_probs = [p.item() * 100 for p in top_probs]
            top_classes = [c.item() for c in top_classes]
            
            # ESTRATEGIA MEJORADA: Verificar si alguna de las top-K es un perro
            perros_detectados = []
            confianza_total_perros = 0.0
            
            for idx, (prob, clase) in enumerate(zip(top_probs, top_classes)):
                es_perro = self.DOG_CLASSES_RANGE[0] <= clase <= self.DOG_CLASSES_RANGE[1]
                if es_perro:
                    nombre = IMAGENET_CLASSES.get(clase, f'Perro_Clase_{clase}')
                    perros_detectados.append({
                        'clase': clase,
                        'nombre': nombre,
                        'confianza': prob,
                        'posicion': idx + 1
                    })
                    confianza_total_perros += prob
            
            # Determinar si la imagen es válida
            tiene_perro = len(perros_detectados) > 0
            
            if tiene_perro:
                # Usar el perro con mayor confianza
                mejor_perro = perros_detectados[0]
                confianza_principal = mejor_perro['confianza']
                nombre_clase = mejor_perro['nombre']
                clase_id = mejor_perro['clase']
                
                # Validar confianza mínima
                # Si hay múltiples perros detectados, ser más permisivo
                if len(perros_detectados) > 1:
                    # Si hay múltiples clases de perro, sumar confianzas
                    confianza_efectiva = confianza_total_perros
                    mensaje_extra = f" ({len(perros_detectados)} razas detectadas, confianza combinada: {confianza_total_perros:.1f}%)"
                else:
                    confianza_efectiva = confianza_principal
                    mensaje_extra = ""
                
                es_valido = confianza_efectiva >= self.MIN_CONFIDENCE
                
                if es_valido:
                    mensaje = f'Canino detectado: {nombre_clase}{mensaje_extra}'
                    logger.info(f"✓ Validación exitosa: {nombre_clase} ({confianza_principal:.1f}%){mensaje_extra}")
                else:
                    mensaje = f'Canino detectado pero con muy baja confianza ({confianza_efectiva:.1f}%)'
                    logger.warning(f"⚠ Confianza muy baja: {nombre_clase} ({confianza_principal:.1f}%)")
                
                return {
                    'es_canino': es_valido,
                    'confianza': round(confianza_principal, 2),
                    'confianza_total': round(confianza_total_perros, 2) if len(perros_detectados) > 1 else round(confianza_principal, 2),
                    'clase_id': clase_id,
                    'objeto_detectado': nombre_clase,
                    'perros_detectados': perros_detectados,
                    'mensaje': mensaje
                }
            else:
                # No se detectó ningún perro en top-K
                top_clase = top_classes[0]
                top_prob = top_probs[0]
                nombre_clase = IMAGENET_CLASSES.get(top_clase, f'Clase_{top_clase}')
                mensaje = f'No es un canino. Detectado: {nombre_clase} ({top_prob:.1f}%)'
                logger.info(f"✗ Imagen rechazada: {nombre_clase} ({top_prob:.1f}%) - No hay perros en top-{self.TOP_K}")
                
                return {
                    'es_canino': False,
                    'confianza': 0.0,
                    'confianza_total': 0.0,
                    'clase_id': top_clase,
                    'objeto_detectado': nombre_clase,
                    'perros_detectados': [],
                    'mensaje': mensaje
                }
            
        except Exception as e:
            logger.error(f"Error durante validación de imagen: {e}", exc_info=True)
            # En caso de error, rechazar la imagen por seguridad
            return {
                'es_canino': False,
                'confianza': 0.0,
                'clase_id': None,
                'objeto_detectado': 'Error',
                'mensaje': f'Error al procesar imagen: {str(e)}'
            }
    
    def _cargar_imagen(self, imagen_input: Union[bytes, str, Any]) -> Image.Image:
        """
        Carga una imagen desde diferentes tipos de input con preprocesamiento mejorado.
        
        Args:
            imagen_input: Bytes, path, PIL Image, o Django UploadedFile
            
        Returns:
            PIL.Image: Imagen cargada en modo RGB con orientación corregida, o None si falla
        """
        try:
            img = None
            
            # Si ya es una imagen PIL
            if isinstance(imagen_input, Image.Image):
                img = imagen_input
            
            # Si es bytes
            elif isinstance(imagen_input, bytes):
                img = Image.open(BytesIO(imagen_input))
            
            # Si es un path (str)
            elif isinstance(imagen_input, str):
                img = Image.open(imagen_input)
            
            # Si es un Django UploadedFile
            elif hasattr(imagen_input, 'read'):
                # Leer el contenido del archivo
                contenido = imagen_input.read()
                # IMPORTANTE: Resetear el puntero del archivo para futuros usos
                if hasattr(imagen_input, 'seek'):
                    imagen_input.seek(0)
                img = Image.open(BytesIO(contenido))
            
            else:
                logger.error(f"Tipo de input no soportado: {type(imagen_input)}")
                return None
            
            # Corregir orientación EXIF si existe
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception as e:
                logger.debug(f"No se pudo corregir orientación EXIF: {e}")
            
            # Convertir a RGB
            img = img.convert('RGB')
            
            # Mejorar contraste si la imagen es muy oscura o muy clara
            try:
                from PIL import ImageEnhance
                np_img = np.array(img)
                brightness = np_img.mean()
                
                # Si la imagen es muy oscura (< 80) o muy clara (> 200), ajustar
                if brightness < 80:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(1.3)  # Aumentar brillo 30%
                    logger.debug(f"Imagen oscura detectada (brillo: {brightness:.1f}), ajustando brillo")
                elif brightness > 200:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.85)  # Reducir brillo 15%
                    logger.debug(f"Imagen muy clara detectada (brillo: {brightness:.1f}), ajustando brillo")
                
                # Mejorar contraste ligeramente
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)  # Aumentar contraste 10%
                
            except Exception as e:
                logger.debug(f"No se pudo mejorar contraste/brillo: {e}")
            
            return img
                
        except Exception as e:
            logger.error(f"Error al cargar imagen: {e}", exc_info=True)
            return None
    
    def validar_desde_bytes(self, imagen_bytes: bytes) -> Dict:
        """
        Método de conveniencia para validar desde bytes (usado con base64).
        
        Args:
            imagen_bytes: Imagen en formato bytes
            
        Returns:
            dict: Resultado de validación
        """
        return self.validar_imagen(imagen_bytes)
    
    def validar_desde_file(self, file: Any) -> Dict:
        """
        Método de conveniencia para validar desde Django UploadedFile.
        
        Args:
            file: Django UploadedFile
            
        Returns:
            dict: Resultado de validación
        """
        return self.validar_imagen(file)


# Diccionario de clases de ImageNet
# Incluye las 118 razas de perros (151-268) y algunas clases comunes NO caninas
IMAGENET_CLASSES = {
    # Razas de perros (151-268)
    151: "Chihuahua",
    152: "Japanese_spaniel",
    153: "Maltese_dog",
    154: "Pekinese",
    155: "Shih-Tzu",
    156: "Blenheim_spaniel",
    157: "Papillon",
    158: "Toy_terrier",
    159: "Rhodesian_ridgeback",
    160: "Afghan_hound",
    161: "Basset",
    162: "Beagle",
    163: "Bloodhound",
    164: "Bluetick",
    165: "Black-and-tan_coonhound",
    166: "Walker_hound",
    167: "English_foxhound",
    168: "Redbone",
    169: "Borzoi",
    170: "Irish_wolfhound",
    171: "Italian_greyhound",
    172: "Whippet",
    173: "Ibizan_hound",
    174: "Norwegian_elkhound",
    175: "Otterhound",
    176: "Saluki",
    177: "Scottish_deerhound",
    178: "Weimaraner",
    179: "Staffordshire_bullterrier",
    180: "American_Staffordshire_terrier",
    181: "Bedlington_terrier",
    182: "Border_terrier",
    183: "Kerry_blue_terrier",
    184: "Irish_terrier",
    185: "Norfolk_terrier",
    186: "Norwich_terrier",
    187: "Yorkshire_terrier",
    188: "Wire-haired_fox_terrier",
    189: "Lakeland_terrier",
    190: "Sealyham_terrier",
    191: "Airedale",
    192: "Cairn",
    193: "Australian_terrier",
    194: "Dandie_Dinmont",
    195: "Boston_bull",
    196: "Miniature_schnauzer",
    197: "Giant_schnauzer",
    198: "Standard_schnauzer",
    199: "Scotch_terrier",
    200: "Tibetan_terrier",
    201: "Silky_terrier",
    202: "Soft-coated_wheaten_terrier",
    203: "West_Highland_white_terrier",
    204: "Lhasa",
    205: "Flat-coated_retriever",
    206: "Curly-coated_retriever",
    207: "Golden_retriever",
    208: "Labrador_retriever",
    209: "Chesapeake_Bay_retriever",
    210: "German_short-haired_pointer",
    211: "Vizsla",
    212: "English_setter",
    213: "Irish_setter",
    214: "Gordon_setter",
    215: "Brittany_spaniel",
    216: "Clumber",
    217: "English_springer",
    218: "Welsh_springer_spaniel",
    219: "Cocker_spaniel",
    220: "Sussex_spaniel",
    221: "Irish_water_spaniel",
    222: "Kuvasz",
    223: "Schipperke",
    224: "Groenendael",
    225: "Malinois",
    226: "Briard",
    227: "Kelpie",
    228: "Komondor",
    229: "Old_English_sheepdog",
    230: "Shetland_sheepdog",
    231: "Collie",
    232: "Border_collie",
    233: "Bouvier_des_Flandres",
    234: "Rottweiler",
    235: "German_shepherd",
    236: "Doberman",
    237: "Miniature_pinscher",
    238: "Greater_Swiss_Mountain_dog",
    239: "Bernese_mountain_dog",
    240: "Appenzeller",
    241: "EntleBucher",
    242: "Boxer",
    243: "Bull_mastiff",
    244: "Tibetan_mastiff",
    245: "French_bulldog",
    246: "Great_Dane",
    247: "Saint_Bernard",
    248: "Eskimo_dog",
    249: "Malamute",
    250: "Siberian_husky",
    251: "Dalmatian",
    252: "Affenpinscher",
    253: "Basenji",
    254: "Pug",
    255: "Leonberg",
    256: "Newfoundland",
    257: "Great_Pyrenees",
    258: "Samoyed",
    259: "Pomeranian",
    260: "Chow",
    261: "Keeshond",
    262: "Brabancon_griffon",
    263: "Pembroke",
    264: "Cardigan",
    265: "Toy_poodle",
    266: "Miniature_poodle",
    267: "Standard_poodle",
    268: "Mexican_hairless",
    
    # Clases NO caninas comunes (para referencia)
    281: "Gato_atigrado",
    282: "Gato_tigre",
    283: "Gato_persa",
    284: "Gato_siamés",
    285: "Gato_egipcio",
    340: "Cebra",
    341: "Cerdo",
    386: "Elefante_africano",
    387: "Elefante_indio",
    497: "Iglesia",
    498: "Mosaico",
    499: "Pantalla",
    504: "Escritorio",
    924: "Plato",
    504: "Taza_café",
    # Agregar más según necesidad
}


# Instancia global singleton (lazy loading)
_validator_instance = None


def get_validator() -> CanineValidator:
    """
    Obtiene la instancia singleton del validador.
    Útil para reutilizar el modelo cargado sin recargarlo cada vez.
    
    Returns:
        CanineValidator: Instancia del validador
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = CanineValidator()
    return _validator_instance
