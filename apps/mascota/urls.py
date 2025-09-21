from django.urls import path
from apps.mascota.views.mascota import main_register

app_name='mascota'

urlpatterns = [
  # registro principal de mascota
  path('mascota/', main_register, name='main_register'),
]