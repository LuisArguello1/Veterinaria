from django.urls import path
from apps.autenticacion.views.temp import paleta
from apps.autenticacion.views.dashboard import Dashboard

app_name='auth'

urlpatterns = [

  # Para ver la paleta de colores ingresar en esta url autenticacion/paleta/
  path('',Dashboard ,name="Dashboard"),
  path('paleta/',paleta ,name="paleta"),

]