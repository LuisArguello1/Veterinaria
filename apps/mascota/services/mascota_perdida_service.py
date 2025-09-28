"""
Servicio para la gestión de mascotas perdidas
Maneja la lógica de negocio para reportar mascotas perdidas y encontradas
"""
from django.utils import timezone
# Removed GIS dependencies - using simple location tracking instead
from typing import Dict, Optional, Tuple
import logging
from .email_service import EmailService

logger = logging.getLogger(__name__)


class MascotaPerdidaService:
    """Servicio para manejar la lógica de mascotas perdidas"""
    
    @staticmethod
    def reportar_como_perdida(mascota, usuario_reporte, ubicacion_perdida: Optional[str] = None) -> Tuple[bool, str]:
        """
        Reporta una mascota como perdida
        
        Args:
            mascota: Instancia del modelo Mascota
            usuario_reporte: Usuario que reporta (debe ser el propietario)
            ubicacion_perdida: Descripción de la ubicación donde se perdió
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar que solo el propietario puede reportar su mascota
            if mascota.propietario != usuario_reporte:
                return False, "Solo el propietario puede reportar su mascota como perdida"
            
            # Verificar si ya está reportada como perdida
            if mascota.reportar_perdida:
                return False, f"{mascota.nombre} ya está reportada como perdida"
            
            # Marcar como perdida
            mascota.reportar_perdida = True
            mascota.save(update_fields=['reportar_perdida'])
            
            # Enviar confirmación al propietario
            EmailService.enviar_confirmacion_reporte_perdida(mascota)
            
            # Enviar alerta a todos los usuarios
            EmailService.enviar_alerta_mascota_perdida(mascota, ubicacion_perdida)
            
            logger.info(f"Mascota {mascota.nombre} (ID: {mascota.id}) reportada como perdida por {usuario_reporte.username}")
            
            return True, f"{mascota.nombre} ha sido reportada como perdida. Se ha enviado una alerta a todos los usuarios."
            
        except Exception as e:
            logger.error(f"Error reportando mascota perdida: {str(e)}")
            return False, f"Error interno del servidor: {str(e)}"
    
    @staticmethod
    def reportar_como_encontrada(mascota, ip_address: Optional[str] = None, user_agent: Optional[str] = None, ubicacion_data: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Reporta una mascota como encontrada
        
        Args:
            mascota: Instancia del modelo Mascota
            ip_address: Dirección IP del usuario que encontró la mascota
            user_agent: User agent del navegador
            ubicacion_data: Diccionario con datos de geolocalización
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar que la mascota esté reportada como perdida
            if not mascota.reportar_perdida:
                return False, f"{mascota.nombre} no está reportada como perdida"
            
            # Obtener datos de ubicación y tiempo del encuentro
            datos_encuentro = MascotaPerdidaService._obtener_datos_encuentro(ip_address, user_agent, ubicacion_data)
            
            # Marcar como encontrada (quitar el flag de perdida)
            mascota.reportar_perdida = False
            mascota.save(update_fields=['reportar_perdida'])
            
            # Enviar notificación al propietario
            exito_email = EmailService.enviar_notificacion_mascota_encontrada(mascota, datos_encuentro)
            
            mensaje_base = f"¡{mascota.nombre} ha sido reportada como encontrada! El propietario ha sido notificado."
            
            if not exito_email:
                mensaje_base += " (Nota: No se pudo enviar el email de notificación)"
            
            logger.info(f"Mascota {mascota.nombre} (ID: {mascota.id}) reportada como encontrada")
            
            return True, mensaje_base
            
        except Exception as e:
            logger.error(f"Error reportando mascota encontrada: {str(e)}")
            return False, f"Error interno del servidor: {str(e)}"
    
    @staticmethod
    def cancelar_reporte_perdida(mascota, usuario_cancelacion) -> Tuple[bool, str]:
        """
        Cancela el reporte de mascota perdida
        
        Args:
            mascota: Instancia del modelo Mascota
            usuario_cancelacion: Usuario que cancela (debe ser el propietario)
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar que solo el propietario puede cancelar
            if mascota.propietario != usuario_cancelacion:
                return False, "Solo el propietario puede cancelar el reporte de su mascota"
            
            # Verificar que esté reportada como perdida
            if not mascota.reportar_perdida:
                return False, f"{mascota.nombre} no está reportada como perdida"
            
            # Cancelar reporte
            mascota.reportar_perdida = False
            mascota.save(update_fields=['reportar_perdida'])
            
            logger.info(f"Reporte de mascota perdida cancelado para {mascota.nombre} (ID: {mascota.id}) por {usuario_cancelacion.username}")
            
            return True, f"El reporte de {mascota.nombre} como perdida ha sido cancelado."
            
        except Exception as e:
            logger.error(f"Error cancelando reporte de mascota perdida: {str(e)}")
            return False, f"Error interno del servidor: {str(e)}"
    
    @staticmethod
    def _obtener_datos_encuentro(ip_address: Optional[str], user_agent: Optional[str], ubicacion_data: Optional[Dict] = None) -> Dict:
        """
        Obtiene datos del encuentro para incluir en el email
        
        Args:
            ip_address: Dirección IP
            user_agent: User agent del navegador
            ubicacion_data: Datos de geolocalización del dispositivo
            
        Returns:
            Dict: Datos del encuentro
        """
        datos = {
            'fecha_hora': timezone.now(),
            'ubicacion_aproximada': None,
            'coordenadas': None,
            'precision_ubicacion': None,
            'ip_address': ip_address,
            'dispositivo_info': None
        }
        
        # Procesar datos de geolocalización del dispositivo (GPS)
        if ubicacion_data:
            try:
                latitud = ubicacion_data.get('latitud')
                longitud = ubicacion_data.get('longitud')
                precision = ubicacion_data.get('precision')
                direccion = ubicacion_data.get('direccion')
                
                if latitud and longitud:
                    datos['coordenadas'] = {
                        'latitud': float(latitud),
                        'longitud': float(longitud)
                    }
                    
                    if precision:
                        datos['precision_ubicacion'] = f"{precision:.0f} metros"
                    
                    # Usar la dirección si está disponible, sino las coordenadas
                    if direccion:
                        datos['ubicacion_aproximada'] = direccion
                    else:
                        datos['ubicacion_aproximada'] = f"Coordenadas: {latitud:.6f}, {longitud:.6f}"
                        
                    logger.info(f"📍 Ubicación GPS procesada: {datos['ubicacion_aproximada']}")
                        
            except Exception as e:
                logger.error(f"Error procesando datos de geolocalización: {str(e)}")
        
        # Ubicación simple por IP como fallback (sin GIS)
        if not datos['ubicacion_aproximada'] and ip_address:
            try:
                # Ubicación básica - podríamos usar un servicio externo simple aquí
                datos['ubicacion_aproximada'] = "Ubicación aproximada registrada por IP"
            except Exception as e:
                logger.debug(f"No se pudo obtener ubicación por IP: {str(e)}")
        
        # Parsear información básica del dispositivo
        if user_agent:
            try:
                # Información básica del dispositivo/navegador
                if 'Mobile' in user_agent:
                    datos['dispositivo_info'] = 'Dispositivo móvil'
                elif 'Tablet' in user_agent:
                    datos['dispositivo_info'] = 'Tablet'
                else:
                    datos['dispositivo_info'] = 'Computadora'
            except Exception as e:
                logger.debug(f"No se pudo parsear user agent: {str(e)}")
        
        return datos
    
    @staticmethod
    def obtener_mascotas_perdidas(usuario_actual=None):
        """
        Obtiene la lista de mascotas reportadas como perdidas
        
        Args:
            usuario_actual: Usuario actual (para filtrar sus propias mascotas si es necesario)
            
        Returns:
            QuerySet: Mascotas perdidas
        """
        from ..models import Mascota
        
        queryset = Mascota.objects.filter(reportar_perdida=True).select_related('propietario')
        
        # Opcional: filtrar mascotas del usuario actual si se proporciona
        if usuario_actual:
            # Podríamos excluir las mascotas del usuario actual para mostrar solo las de otros
            # queryset = queryset.exclude(propietario=usuario_actual)
            pass
        
        return queryset.order_by('-updated_at')
    
    @staticmethod
    def verificar_puede_reportar_perdida(mascota, usuario) -> Tuple[bool, str]:
        """
        Verifica si un usuario puede reportar una mascota como perdida
        
        Args:
            mascota: Instancia del modelo Mascota
            usuario: Usuario que quiere reportar
            
        Returns:
            Tuple[bool, str]: (puede_reportar, mensaje)
        """
        # Solo el propietario puede reportar
        if mascota.propietario != usuario:
            return False, "Solo el propietario puede reportar su mascota como perdida"
        
        # No se puede reportar si ya está perdida
        if mascota.reportar_perdida:
            return False, f"{mascota.nombre} ya está reportada como perdida"
        
        return True, "Puede reportar como perdida"
    
    @staticmethod
    def verificar_puede_reportar_encontrada(mascota) -> Tuple[bool, str]:
        """
        Verifica si se puede reportar una mascota como encontrada
        
        Args:
            mascota: Instancia del modelo Mascota
            
        Returns:
            Tuple[bool, str]: (puede_reportar, mensaje)
        """
        # Solo se puede reportar como encontrada si está perdida
        if not mascota.reportar_perdida:
            return False, f"{mascota.nombre} no está reportada como perdida"
        
        return True, "Puede reportar como encontrada"