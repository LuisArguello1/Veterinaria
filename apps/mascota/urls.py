from django.urls import path
from apps.mascota.views.mascota import main_register
from apps.mascota.views.create_mascota import MascotaCreateView
from apps.mascota.views.update_mascota import MascotaUpdateView
from apps.mascota.views.biometria import (
    BiometriaView, 
    upload_biometria_image, 
    upload_biometria_base64,
    delete_imagen, 
    get_mascota_stats, 
    train_model,
    ScannerView, 
    upload_image_for_recognition,
    get_user_pets,
    MascotaDetailView,
)

from apps.mascota.views.delete_mascota import MascotaDeleteView, BiometriaDeleteView

from apps.mascota.views.historial_views import (
    HistorialMedicoListView,
    HistorialMedicoCreateView,
    RegistroVacunaCreateView,
    CartillaVacunacionView,
)

from apps.mascota.views.qr_views import (
    mascota_info_publica,
    generar_qr_mascota,
    descargar_qr_mascota
)

from apps.mascota.views.mascota_perdida_views import (
    reportar_perdida,
    cancelar_reporte_perdida,
    reportar_encontrada,
    verificar_estado_perdida,
    listar_mascotas_perdidas,
    api_mascotas_perdidas
)



app_name='mascota'

urlpatterns = [
    # Registro principal de mascota
    path('mascota/', main_register, name='main_register'),
    
    # Crear nueva mascota (solo OWNER y ADMIN)
    path('mascota/create/', MascotaCreateView.as_view(), name='create_mascota'),
    
    # Editar mascota
    path('mascota/<int:pk>/edit/', MascotaUpdateView.as_view(), name='edit_mascota'),
    
    # Detalle de mascota
    path('mascota/<int:pk>/', MascotaDetailView.as_view(), name='detalle'),
    
    # Biometría de mascota
    path('mascota/<int:pk>/biometria/', BiometriaView.as_view(), name='biometria'),
    path('biometria/', BiometriaView.as_view(), name='biometria_direct'),
    path('mascota/upload-biometria/', upload_biometria_image, name='upload_biometria'),
    path('mascota/upload-biometria-base64/', upload_biometria_base64, name='upload_biometria_base64'),
    path('mascota/delete-imagen/<int:pk>/', delete_imagen, name='delete_imagen'),
    path('mascota/get-stats/<int:pk>/', get_mascota_stats, name='get_mascota_stats'),
    path('mascota/train-model/<int:pk>/', train_model, name='train_model'),

    # Delete
    path('mascota/<int:pk>/delete/', MascotaDeleteView.as_view(), name='delete_mascota'),
    path('mascota/<int:pk>/delete-biometria/', BiometriaDeleteView.as_view(), name='delete_biometria'),
    
    # Historial Médico y Vacunación
    path('mascota/<int:mascota_pk>/historial/', HistorialMedicoListView.as_view(), name='historial_list'),
    path('mascota/<int:mascota_pk>/historial/nuevo/', HistorialMedicoCreateView.as_view(), name='historial_create'),
    path('mascota/<int:mascota_pk>/vacunas/', CartillaVacunacionView.as_view(), name='cartilla_vacunacion'),
    path('mascota/<int:mascota_pk>/vacunas/registrar/', RegistroVacunaCreateView.as_view(), name='registrar_vacuna'),

    # Escáner de reconocimiento
    path('scanner/', ScannerView.as_view(), name='scanner'),
    path('scanner/upload-recognition/', upload_image_for_recognition, name='upload_recognition'),
    
    # API para obtener mascotas del usuario
    path('mascota/get-user-pets/', get_user_pets, name='get_user_pets'),
    
    # Sistema de códigos QR
    path('qr/info/<uuid:mascota_uuid>/', mascota_info_publica, name='qr_info_publica'),
    path('mascota/<int:mascota_id>/qr/generar/', generar_qr_mascota, name='generar_qr'),
    path('mascota/<int:mascota_id>/qr/descargar/', descargar_qr_mascota, name='descargar_qr'),
    
    # Sistema de mascotas perdidas
    path('mascota/<int:mascota_id>/reportar-perdida/', reportar_perdida, name='reportar_perdida'),
    path('mascota/<int:mascota_id>/cancelar-perdida/', cancelar_reporte_perdida, name='cancelar_reporte_perdida'),
    path('perdida/<uuid:mascota_uuid>/reportar-encontrada/', reportar_encontrada, name='reportar_encontrada'),
    path('perdida/<uuid:mascota_uuid>/verificar-estado/', verificar_estado_perdida, name='verificar_estado_perdida'),
    path('mascotas-perdidas/', listar_mascotas_perdidas, name='listar_mascotas_perdidas'),
    path('api/mascotas-perdidas/', api_mascotas_perdidas, name='api_mascotas_perdidas'),
]