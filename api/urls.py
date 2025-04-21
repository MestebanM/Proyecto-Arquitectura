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
router.register('eventos', EventoMascotaViewSet, basename='evento')
router.register('recorridos', RecorridoMascotaViewSet, basename='recorrido')



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

    path('mi-perfil/', UsuarioConMascotasView.as_view(), name='mi_perfil'),

    path('eliminar-cuenta/', EliminarCuentaView.as_view(), name='eliminar_cuenta'),

    path('mascotas-atendidas/', MascotasAtendidasView.as_view(), name='mascotas_atendidas'),

    path('veterinarios-por-clinica/', VeterinariosPorClinicaView.as_view(), name='veterinarios_por_clinica'),

    path('clinicas-disponibles/', ClinicasDisponiblesView.as_view(), name='clinicas_disponibles'),

    path('vacunas/mascota/<int:mascota_id>/', VacunasPorMascotaView.as_view(), name='vacunas_por_mascota'),

    path('vacunas/agregar-directo/', AgregarVacunaDirectaView.as_view(), name='vacuna_directa'),

    path('mascotas/actualizar/<int:mascota_id>/', ActualizarMascotaView.as_view(), name='actualizar_mascota'),

    path('usuarios/', AdministrarUsuariosView.as_view(), name='crud_usuarios'),

    path('usuarios/<int:user_id>/', AdministrarUsuariosView.as_view(), name='actualizar_usuario_admin'),

    path('mascotas/usuario/<int:usuario_id>/', MascotasPorUsuarioView.as_view(), name='mascotas_por_usuario'),

    path('mascotas/historial/<int:mascota_id>/', HistorialMascotaView.as_view(), name='historial_mascota'),

    path('mascotas/estadisticas/<int:mascota_id>/', EstadisticasEventosView.as_view(), name='estadisticas_eventos'),

    path('vacunas/total-por-fecha/<int:mascota_id>/', TotalVacunasPorFechaView.as_view(), name='total_vacunas_por_fecha'),

    path('mascotas/visitas-veterinario/<int:mascota_id>/', TotalVisitasVeterinarioView.as_view(), name='total_visitas_veterinario'),

    path('mascotas/consolidado-eventos/<int:mascota_id>/', ConsolidadoEventosMascotaView.as_view(), name='consolidado_eventos'),

    path('mascotas/promedio-recorrido/<int:mascota_id>/', PromedioRecorridoDiarioView.as_view(), name='promedio_recorrido_diario'),


]
