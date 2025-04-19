from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet)
router.register('mascotas', MascotaViewSet, basename='mascota')
router.register('historias', HistoriaMedicaViewSet, basename='historia')
router.register('vacunas', VacunaViewSet, basename='vacuna')
router.register('recordatorios', RecordatorioViewSet, basename='recordatorio')
router.register('veterinarias', VeterinariaViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Registro e inicio de sesión
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('login/', LoginUsuarioView.as_view(), name='login_usuario'),

    # Actualización de usuario (perfil)
    path('actualizar-usuario/', ActualizarUsuarioView.as_view(), name='actualizar_usuario'),

    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),

    # Vista para que un veterinario vea las historias de una mascota en particular
    path('historias/mascota/<int:mascota_id>/', HistoriasPorMascotaView.as_view(), name='historias_por_mascota'),
]
