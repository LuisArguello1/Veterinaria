/**
 * Sistema de Notificaciones
 * Gestiona el contador en tiempo real de notificaciones sin leer
 */

class NotificationManager {
    constructor() {
        this.badge = document.getElementById('notification-badge');
        this.bell = document.getElementById('notification-bell');
        this.sidebarBadge = document.getElementById('sidebar-notification-badge');
        this.updateInterval = 30000; // 30 segundos
        this.init();
    }

    init() {
        if (!this.badge || !this.bell) return;
        
        // Actualizar inmediatamente
        this.updateCount();
        
        // Actualizar periódicamente
        setInterval(() => this.updateCount(), this.updateInterval);
        
        // Agregar animación al bell cuando hay notificaciones
        this.bell.addEventListener('mouseenter', () => {
            this.bell.querySelector('i').classList.add('animate-bounce');
        });
        
        this.bell.addEventListener('mouseleave', () => {
            this.bell.querySelector('i').classList.remove('animate-bounce');
        });
    }

    async updateCount() {
        try {
            const response = await fetch('/auth/api/notifications/count/');
            if (!response.ok) throw new Error('Error al obtener notificaciones');
            
            const data = await response.json();
            this.displayCount(data.count);
            
            // Animar si hay nuevas notificaciones
            if (data.has_notifications && data.count > 0) {
                this.animateBell();
            }
        } catch (error) {
            console.error('Error al actualizar notificaciones:', error);
        }
    }

    displayCount(count) {
        if (count > 0) {
            // Badge en el navbar
            if (this.badge) {
                this.badge.textContent = count > 99 ? '99+' : count;
                this.badge.classList.remove('hidden');
            }
            
            // Badge en el sidebar
            if (this.sidebarBadge) {
                this.sidebarBadge.textContent = count > 99 ? '99+' : count;
                this.sidebarBadge.classList.remove('hidden');
            }
        } else {
            if (this.badge) this.badge.classList.add('hidden');
            if (this.sidebarBadge) this.sidebarBadge.classList.add('hidden');
        }
    }

    animateBell() {
        const icon = this.bell.querySelector('i');
        icon.classList.add('animate-pulse');
        setTimeout(() => {
            icon.classList.remove('animate-pulse');
        }, 2000);
    }

    /**
     * Marcar notificación como leída (AJAX)
     */
    static async markAsRead(notificationId) {
        try {
            const response = await fetch(`/auth/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });
            
            if (!response.ok) throw new Error('Error al marcar como leída');
            
            const data = await response.json();
            return data.success;
        } catch (error) {
            console.error('Error:', error);
            return false;
        }
    }

    /**
     * Marcar todas como leídas (AJAX)
     */
    static async markAllAsRead() {
        try {
            const response = await fetch('/auth/notifications/read-all/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });
            
            if (!response.ok) throw new Error('Error al marcar todas como leídas');
            
            const data = await response.json();
            
            // Recargar la página para reflejar los cambios
            window.location.reload();
            
            return data.success;
        } catch (error) {
            console.error('Error:', error);
            return false;
        }
    }

    /**
     * Eliminar notificación (AJAX)
     */
    static async deleteNotification(notificationId) {
        if (!confirm('¿Estás seguro de que deseas eliminar esta notificación?')) {
            return false;
        }
        
        try {
            const response = await fetch(`/auth/notifications/${notificationId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });
            
            if (!response.ok) throw new Error('Error al eliminar notificación');
            
            const data = await response.json();
            
            // Remover el elemento del DOM con animación
            const element = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (element) {
                element.style.opacity = '0';
                element.style.transform = 'translateX(100px)';
                setTimeout(() => element.remove(), 300);
            }
            
            return data.success;
        } catch (error) {
            console.error('Error:', error);
            return false;
        }
    }

    /**
     * Obtener token CSRF
     */
    static getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si el usuario está autenticado
    if (document.getElementById('notification-badge')) {
        window.notificationManager = new NotificationManager();
    }
});

// Exponer funciones útiles globalmente
window.NotificationManager = NotificationManager;
