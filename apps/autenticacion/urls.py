from django.urls import path
from apps.autenticacion.views.dashboard import Dashboard
from apps.autenticacion.views.login import LoginView, LogoutView
from apps.autenticacion.views.profile import ProfileView, ProfileUpdateView, ProfilePasswordChangeView
from apps.autenticacion.views.users import (
  UserListView, 
  UserDetailView, 
  UserCreateView, 
  UserUpdateView, 
  UserDeleteView,
  ChangePasswordView
)
from apps.autenticacion.views.register import RegisterView
from apps.autenticacion.views.notifications import (
    NotificationListView,
    NotificationMarkAsReadView,
    NotificationMarkAllAsReadView,
    NotificationArchiveView,
    NotificationDeleteView,
    NotificationCountView,
    NotificationRecentView,
)

app_name='auth'

urlpatterns = [
  # Autenticación
  path('', LoginView.as_view(), name='login'),
  path('logout/', LogoutView.as_view(), name='logout'),
  
  # Dashboard principal
  path('dashboard/', Dashboard, name="Dashboard"),
    
  # Perfil de usuario
  path('profile/', ProfileView.as_view(), name='profile'),
  path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
  path('profile/password/', ProfilePasswordChangeView.as_view(), name='profile_password'),

  # Registro público para dueños de mascotas
  path('register/', RegisterView.as_view(), name='register'),
    
  # Gestión de usuarios (CRUD)
  path('users/', UserListView.as_view(), name='users_list'),
  path('users/add/', UserCreateView.as_view(), name='user_create'),
  path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
  path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
  path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
  path('users/<int:pk>/password/', ChangePasswordView.as_view(), name='user_password_change'),
  
  # Sistema de notificaciones
  path('notifications/', NotificationListView.as_view(), name='notifications'),
  path('notifications/<int:pk>/read/', NotificationMarkAsReadView.as_view(), name='notification_mark_read'),
  path('notifications/read-all/', NotificationMarkAllAsReadView.as_view(), name='notification_mark_all_read'),
  path('notifications/<int:pk>/archive/', NotificationArchiveView.as_view(), name='notification_archive'),
  path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification_delete'),
  
  # API de notificaciones
  path('api/notifications/count/', NotificationCountView.as_view(), name='api_notification_count'),
  path('api/notifications/recent/', NotificationRecentView.as_view(), name='api_notification_recent'),
]