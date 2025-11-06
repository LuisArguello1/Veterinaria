document.addEventListener('DOMContentLoaded', function() {
    const notificationsToggle = document.getElementById('notifications-toggle');
    const notificationsDropdown = document.getElementById('notifications-dropdown');
    const notificationsList = document.getElementById('notifications-list');
    const notificationsBadge = document.getElementById('notifications-badge');
    const markAllReadBtn = document.getElementById('mark-all-read');

    // Si no existen los elementos, el usuario no está autenticado
    if (!notificationsToggle || !notificationsDropdown) {
        return;
    }

    let isDropdownOpen = false;

    // Toggle dropdown
    if (notificationsToggle) {
        notificationsToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            isDropdownOpen = !isDropdownOpen;
            
            if (isDropdownOpen) {
                notificationsDropdown.classList.remove('hidden');
                // Desactivar scroll del body
                document.body.style.overflow = 'hidden';
                document.body.classList.add('notifications-open');
                // Agregar padding para compensar el scrollbar en desktop
                if (window.innerWidth > 768) {
                    document.body.style.paddingRight = getScrollbarWidth() + 'px';
                }
                loadNotifications();
            } else {
                notificationsDropdown.classList.add('hidden');
                // Reactivar scroll del body
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                document.body.classList.remove('notifications-open');
            }
        });
    }

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (isDropdownOpen && 
            !notificationsDropdown.contains(e.target) && 
            !notificationsToggle.contains(e.target)) {
            notificationsDropdown.classList.add('hidden');
            // Reactivar scroll del body
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            document.body.classList.remove('notifications-open');
            isDropdownOpen = false;
        }
    });
    
    // Cerrar con tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isDropdownOpen) {
            notificationsDropdown.classList.add('hidden');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            document.body.classList.remove('notifications-open');
            isDropdownOpen = false;
        }
    });
    
    // Función para obtener el ancho del scrollbar
    function getScrollbarWidth() {
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll';
        document.body.appendChild(outer);
        const inner = document.createElement('div');
        outer.appendChild(inner);
        const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
        outer.parentNode.removeChild(outer);
        return scrollbarWidth;
    }

    // Cargar notificaciones
    function loadNotifications() {
        fetch('/notifications/list/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            // Mostrar todas las notificaciones (sin límite)
            renderNotifications(data.notifications);
            updateBadge(data.unread_count);
        })
        .catch(error => {
            console.error('Error al cargar notificaciones:', error);
            notificationsList.innerHTML = `
                <div class="p-4 text-center text-danger-500 text-sm">
                    <i class="fas fa-exclamation-triangle mb-2"></i>
                    <p>Error al cargar notificaciones</p>
                </div>
            `;
        });
    }

    // Renderizar notificaciones
    function renderNotifications(notifications) {
        if (notifications.length === 0) {
            notificationsList.innerHTML = `
                <div class="p-6 text-center text-neutral-500 text-sm">
                    <i class="fas fa-inbox text-3xl mb-3 text-neutral-300"></i>
                    <p class="font-medium">No tienes notificaciones</p>
                    <p class="text-xs text-neutral-400 mt-1">Aquí aparecerán tus notificaciones</p>
                </div>
            `;
            toggleScrollIndicator(false);
            return;
        }

        notificationsList.innerHTML = notifications.map(notification => {
            const iconClass = getNotificationIcon(notification.notification_type);
            const colorClass = getNotificationColor(notification.notification_type);
            const date = new Date(notification.created_at).toLocaleDateString('es-ES', {
                day: '2-digit',
                month: 'short',
                hour: '2-digit',
                minute: '2-digit'
            });

            return `
                <div class="notification-item p-4 hover:bg-neutral-50 transition-colors border-b border-neutral-100 last:border-b-0 ${notification.is_read ? 'opacity-70' : ''}" data-id="${notification.id}">
                    <div class="flex gap-3">
                        <div class="flex-shrink-0">
                            <div class="w-10 h-10 rounded-full ${colorClass} flex items-center justify-center shadow-sm">
                                <i class="${iconClass} text-white text-sm"></i>
                            </div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-start justify-between gap-2 mb-1">
                                <h4 class="text-sm font-semibold text-dark-800 ${notification.is_read ? '' : 'font-bold'} leading-tight">${notification.title}</h4>
                                ${!notification.is_read ? '<span class="w-2 h-2 bg-primary-500 rounded-full flex-shrink-0 mt-1"></span>' : ''}
                            </div>
                            <p class="text-xs text-neutral-600 leading-relaxed whitespace-normal break-words mb-2">${notification.message}</p>
                            <div class="flex items-center justify-between gap-2 flex-wrap">
                                <span class="text-xs text-neutral-400">${date}</span>
                                <div class="flex gap-3">
                                    ${!notification.is_read ? `
                                        <button onclick="markAsRead(${notification.id})" class="text-xs text-secondary-600 hover:text-secondary-800 font-medium transition-colors">
                                            <i class="fas fa-check text-[10px] mr-1"></i>Marcar leída
                                        </button>
                                    ` : ''}
                                    <button onclick="deleteNotification(${notification.id})" class="text-xs text-danger-600 hover:text-danger-800 font-medium transition-colors">
                                        <i class="fas fa-trash text-[10px] mr-1"></i>Eliminar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Mostrar indicador de scroll si hay más de 3 notificaciones
        toggleScrollIndicator(notifications.length > 3);
        
        // Agregar listener para detectar cuando se llega al final
        setupScrollListener();
    }
    
    // Mostrar/ocultar indicador de scroll
    function toggleScrollIndicator(show) {
        const footer = document.getElementById('notifications-footer');
        if (footer) {
            if (show) {
                footer.classList.remove('hidden');
            } else {
                footer.classList.add('hidden');
            }
        }
    }
    
    // Configurar listener para scroll
    function setupScrollListener() {
        if (notificationsList) {
            notificationsList.addEventListener('scroll', function() {
                const footer = document.getElementById('notifications-footer');
                if (footer) {
                    const isAtBottom = this.scrollHeight - this.scrollTop <= this.clientHeight + 10;
                    if (isAtBottom) {
                        footer.classList.add('hidden');
                    } else {
                        footer.classList.remove('hidden');
                    }
                }
            });
        }
    }

    // Actualizar badge
    function updateBadge(count) {
        if (count > 0) {
            notificationsBadge.textContent = count > 99 ? '99+' : count;
            notificationsBadge.classList.remove('hidden');
            notificationsBadge.classList.add('flex');
        } else {
            notificationsBadge.classList.add('hidden');
            notificationsBadge.classList.remove('flex');
        }
    }

    // Obtener ícono según tipo
    function getNotificationIcon(type) {
        const icons = {
            'INFO': 'fas fa-info-circle',
            'SUCCESS': 'fas fa-check-circle',
            'WARNING': 'fas fa-exclamation-triangle',
            'ERROR': 'fas fa-times-circle'
        };
        return icons[type] || 'fas fa-bell';
    }

    // Obtener color según tipo
    function getNotificationColor(type) {
        const colors = {
            'INFO': 'bg-primary-500',
            'SUCCESS': 'bg-success-500',
            'WARNING': 'bg-warning-500',
            'ERROR': 'bg-danger-500'
        };
        return colors[type] || 'bg-neutral-500';
    }

    // Marcar como leída
    window.markAsRead = function(notificationId) {
        fetch(`/notifications/${notificationId}/mark-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadNotifications();
            }
        })
        .catch(error => console.error('Error:', error));
    };

    // Eliminar notificación
    window.deleteNotification = function(notificationId) {
        Swal.fire({
            title: '¿Eliminar notificación?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            backdrop: true,
            allowOutsideClick: true
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/notifications/${notificationId}/delete/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadNotifications();
                        Swal.fire({
                            title: '¡Eliminada!',
                            text: 'La notificación ha sido eliminada',
                            icon: 'success',
                            timer: 2000,
                            showConfirmButton: false
                        });
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    };

    // Marcar todas como leídas
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function() {
            fetch('/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadNotifications();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Obtener CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Actualizar notificaciones cada 30 segundos
    setInterval(function() {
        if (!isDropdownOpen) {
            fetch('/notifications/count/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                updateBadge(data.unread_count);
            })
            .catch(error => console.error('Error:', error));
        }
    }, 30000);

    // Cargar contador inicial
    if (notificationsBadge) {
        fetch('/notifications/count/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            updateBadge(data.unread_count);
        })
        .catch(error => console.error('Error:', error));
    }
});