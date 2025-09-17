from django.urls import path
from apps.autenticacion.views.temp import paleta
from apps.autenticacion.views.dashboard import Dashboard
from apps.autenticacion.views.login import LoginView, LogoutView
from apps.autenticacion.views.profile import ProfileView, ProfileUpdateView
from apps.autenticacion.views.users import (
    # Vistas generales de usuarios
    UserListView, UserDetailView, UserCreateView, UserUpdateView, UserDeleteView,
    # Vistas para cambio de contraseña
    ChangePasswordView
)
from apps.autenticacion.views.register import RegisterView

app_name='auth'

urlpatterns = [
  # Autenticación
  path('', LoginView.as_view(), name='login'),  # Login como página principal
  path('logout/', LogoutView.as_view(), name='logout'),
  
  # Dashboard principal
  path('dashboard/', Dashboard, name="Dashboard"),
  path('paleta/', paleta, name="paleta"),
    
  # Perfil de usuario
  path('profile/', ProfileView.as_view(), name='profile'),
  path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
  # Registro público
  path('register/', RegisterView.as_view(), name='register'),
  path('password/change/', ChangePasswordView.as_view(), name='password_change'),
    
  # Gestión de usuarios (CRUD)
  path('users/', UserListView.as_view(), name='users_list'),
  path('users/add/', UserCreateView.as_view(), name='user_create'),
  path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
  path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
  path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
  path('users/<int:pk>/password/', ChangePasswordView.as_view(), name='user_password_change'),
]