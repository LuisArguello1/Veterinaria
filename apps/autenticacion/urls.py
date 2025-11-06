from django.urls import path, include
from apps.autenticacion.views.dashboard import Dashboard
from apps.autenticacion.views.dashboard_admin import admin_dashboard
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
from apps.autenticacion.views.facial_views import (
  FacialBiometryRegisterView,
  DetectFaceView,
  RegisterFacialBiometryView,
  VerifyFacialLoginView,
  DeleteFacialBiometryView,
  ToggleFacialLoginView
)
from apps.autenticacion.views.password_recovery import (
  PasswordRecoveryRequestView,
  PasswordRecoveryDoneView,
  PasswordRecoveryConfirmView,
  PasswordRecoveryCompleteView
)
from apps.autenticacion.views.notifications import (
  NotificationListView,
  NotificationCountView,
  NotificationMarkReadView,
  NotificationMarkAllReadView,
  NotificationDeleteView
)

app_name='auth'

urlpatterns = [
  # Autenticación
  path('', LoginView.as_view(), name='login'),
  path('logout/', LogoutView.as_view(), name='logout'),
  
  # Dashboard principal
  path('dashboard/', Dashboard, name="Dashboard"),
  
  # Dashboard administrativo (solo para admins)
  path('admin-dashboard/', admin_dashboard, name="admin_dashboard"),
    
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
  
  # Reconocimiento facial
  path('profile/facial-biometry/', FacialBiometryRegisterView.as_view(), name='facial_biometry_register'),
  path('api/facial/detect/', DetectFaceView.as_view(), name='facial_detect'),
  path('api/facial/register/', RegisterFacialBiometryView.as_view(), name='facial_register'),
  path('api/facial/verify/', VerifyFacialLoginView.as_view(), name='facial_verify'),
  path('api/facial/delete/', DeleteFacialBiometryView.as_view(), name='facial_delete'),
  path('api/facial/toggle/', ToggleFacialLoginView.as_view(), name='facial_toggle'),
  
  # Recuperación de contraseña
  path('password-recovery/', PasswordRecoveryRequestView.as_view(), name='password_recovery_request'),
  path('password-recovery/done/', PasswordRecoveryDoneView.as_view(), name='password_recovery_done'),
  path('password-recovery/confirm/<uidb64>/<token>/', PasswordRecoveryConfirmView.as_view(), name='password_recovery_confirm'),
  path('password-recovery/complete/', PasswordRecoveryCompleteView.as_view(), name='password_recovery_complete'),
  
  # Notificaciones
  path('notifications/list/', NotificationListView.as_view(), name='notifications_list'),
  path('notifications/count/', NotificationCountView.as_view(), name='notifications_count'),
  path('notifications/<int:notification_id>/mark-read/', NotificationMarkReadView.as_view(), name='notification_mark_read'),
  path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notifications_mark_all_read'),
  path('notifications/<int:notification_id>/delete/', NotificationDeleteView.as_view(), name='notification_delete'),
  
  # APIs para integración con chatbot
  path('api/', include('apps.autenticacion.urls_chatbot')),
]