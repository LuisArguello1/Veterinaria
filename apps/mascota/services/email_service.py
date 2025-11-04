"""
Servicio para el envío de emails relacionados con mascotas perdidas
"""
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailService:
    """Servicio centralizado para el envío de emails del sistema de mascotas perdidas"""
    
    @staticmethod
    def _get_absolute_url(relative_url: Optional[str]) -> Optional[str]:
        """
        Convierte una URL relativa a una URL absoluta
        
        Args:
            relative_url: URL relativa (ej: /media/foto.jpg) o URL absoluta de Azure
            
        Returns:
            URL absoluta (ej: http://localhost:8000/media/foto.jpg) o None
            
        Note:
            Si la URL ya es absoluta (empieza con http:// o https://), 
            la retorna sin cambios. Esto es útil cuando se usa Azure Storage.
        """
        if not relative_url:
            return None
        
        # Si ya es una URL absoluta (Azure Storage, etc.), retornarla sin cambios
        if relative_url.startswith(('http://', 'https://')):
            return relative_url
        
        # Obtener el dominio base desde settings o usar localhost por defecto
        # En producción, configurar BASE_URL en settings.py
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        
        # Asegurarse que la URL relativa empiece con /
        if not relative_url.startswith('/'):
            relative_url = '/' + relative_url
        
        # Construir URL absoluta
        return f"{base_url.rstrip('/')}{relative_url}"
    
    @staticmethod
    def enviar_alerta_mascota_perdida(mascota, ubicacion_perdida: Optional[str] = None) -> bool:
        """
        Envía email a todos los usuarios registrados notificando que una mascota fue reportada como perdida
        
        Args:
            mascota: Instancia del modelo Mascota
            ubicacion_perdida: Ubicación donde se perdió la mascota (opcional)
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            # Obtener todos los usuarios activos con email
            usuarios_activos = User.objects.filter(is_active=True, email__isnull=False).exclude(email='')
            
            if not usuarios_activos.exists():
                logger.warning("No hay usuarios con email para notificar mascota perdida")
                return False
            
            # Preparar contexto para el template
            context = {
                'mascota': mascota,
                'propietario': mascota.propietario,
                'ubicacion_perdida': ubicacion_perdida,
                'foto_url': EmailService._get_absolute_url(mascota.foto_perfil.url) if mascota.foto_perfil else None,
                'contacto_propietario': {
                    'nombre': mascota.propietario.get_full_name() or mascota.propietario.username,
                    'email': mascota.propietario.email,
                    'telefono': getattr(mascota.propietario, 'phone', None)
                }
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/mascota_perdida_alerta.html', context)
            plain_message = strip_tags(html_message)
            
            # Preparar asunto
            subject = f'🚨 Alerta: {mascota.nombre} ha sido reportada como perdida'
            
            # Enviar emails individuales con HTML
            emails_enviados = 0
            for usuario in usuarios_activos:
                # No enviar al propietario de la mascota
                if usuario.id != mascota.propietario.id:
                    try:
                        send_mail(
                            subject=subject,
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[usuario.email],
                            html_message=html_message,
                            fail_silently=False
                        )
                        emails_enviados += 1
                    except Exception as e:
                        logger.error(f"Error enviando email a {usuario.email}: {str(e)}")
            
            if emails_enviados > 0:
                logger.info(f"✅ Alerta de mascota perdida enviada a {emails_enviados} usuarios para {mascota.nombre}")
                print(f"📧 EMAILS ENVIADOS: {emails_enviados} alertas para {mascota.nombre}")
                return True
            else:
                logger.warning(f"❌ No hay destinatarios válidos para alerta de {mascota.nombre}")
                print(f"⚠️ No se enviaron emails para {mascota.nombre}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando alerta de mascota perdida para {mascota.nombre}: {str(e)}")
            return False
    
    @staticmethod
    def enviar_notificacion_mascota_encontrada(mascota, datos_encuentro: Dict) -> bool:
        """
        Envía email al propietario notificando que su mascota fue encontrada
        
        Args:
            mascota: Instancia del modelo Mascota
            datos_encuentro: Diccionario con datos del encuentro (ubicación, hora, etc.)
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            if not mascota.propietario.email:
                logger.warning(f"Propietario de {mascota.nombre} no tiene email configurado")
                return False
            
            # Preparar contexto para el template
            context = {
                'mascota': mascota,
                'propietario': mascota.propietario,
                'datos_encuentro': datos_encuentro,
                'foto_url': EmailService._get_absolute_url(mascota.foto_perfil.url) if mascota.foto_perfil else None,
            }
            
            # Renderizar templates
            html_message = render_to_string('emails/mascota_encontrada_notificacion.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            success = send_mail(
                subject=f'🎉 ¡Buenas noticias! {mascota.nombre} ha sido encontrada',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[mascota.propietario.email],
                html_message=html_message,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Notificación de mascota encontrada enviada a {mascota.propietario.email}")
                return True
            else:
                logger.error(f"Fallo en envío de notificación de mascota encontrada para {mascota.nombre}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando notificación de mascota encontrada para {mascota.nombre}: {str(e)}")
            return False
    
    @staticmethod
    def enviar_confirmacion_reporte_perdida(mascota) -> bool:
        """
        Envía email de confirmación al propietario cuando reporta su mascota como perdida
        
        Args:
            mascota: Instancia del modelo Mascota
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            if not mascota.propietario.email:
                logger.warning(f"Propietario de {mascota.nombre} no tiene email configurado")
                return False
            
            # Preparar contexto
            context = {
                'mascota': mascota,
                'propietario': mascota.propietario,
                'foto_url': EmailService._get_absolute_url(mascota.foto_perfil.url) if mascota.foto_perfil else None,
                'fecha_reporte': timezone.now()
            }
            
            # Renderizar templates
            html_message = render_to_string('emails/confirmacion_reporte_perdida.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            success = send_mail(
                subject=f'Confirmación: {mascota.nombre} ha sido reportada como perdida',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[mascota.propietario.email],
                html_message=html_message,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Confirmación de reporte enviada a {mascota.propietario.email}")
                return True
            else:
                logger.error(f"Fallo en envío de confirmación para {mascota.nombre}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando confirmación de reporte para {mascota.nombre}: {str(e)}")
            return False