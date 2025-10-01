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
  
]