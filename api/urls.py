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
router.register('direcciones', DireccionViewSet, basename='direccion')
router.register('horarios-no-disponibles', HorarioNoDisponibleViewSet, basename='horario')
router.register('control-fisico', ControlFisicoViewSet, basename='control_fisico')
router.register('historial-servicios', HistorialServicioViewSet, basename='historial_servicio')
router.register('paseos-programados', PaseoProgramadoViewSet, basename='paseo_programado')


urlpatterns = [
    path('', include(router.urls)),

    # Autenticación
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('login/', LoginUsuarioView.as_view(), name='login_usuario'),

    # Perfil y cuenta
    path('mi-perfil/', UsuarioConMascotasView.as_view(), name='mi_perfil'),
    path('actualizar-usuario/', ActualizarUsuarioView.as_view(), name='actualizar_usuario'),
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('eliminar-cuenta/', EliminarCuentaView.as_view(), name='eliminar_cuenta'),

    # Gestión de usuarios (admin)
    path('usuarios/admin/', AdministrarUsuariosView.as_view(), name='crud_usuarios'),
    path('usuarios/<int:user_id>/', AdministrarUsuariosView.as_view(), name='actualizar_usuario_admin'),
    path('usuarios/<int:id>/detalle/', UsuarioDetailView.as_view(), name='detalle_usuario'),
    path('veterinarios/', ListaVeterinariosView.as_view(), name='lista_veterinarios'),
    path('cuidadores/', ListaCuidadoresView.as_view(), name='lista_cuidadores'),
    path('duenos/', ListaDuenosView.as_view(), name='lista_duenos'),

    # Mascotas
    path('mascotas/actualizar/<int:mascota_id>/', ActualizarMascotaView.as_view(), name='actualizar_mascota'),
    path('mascotas/usuario/<int:usuario_id>/', MascotasPorUsuarioView.as_view(), name='mascotas_por_usuario'),
    path('mascotas/cuidador/<int:cuidador_id>/', MascotasPorCuidadorView.as_view(), name='mascotas_por_cuidador'),
    path('mascotas/veterinario/<int:vet_id>/', MascotasPorVeterinarioView.as_view(), name='mascotas_por_veterinario'),
    path('mascotas-atendidas/', MascotasAtendidasView.as_view(), name='mascotas_atendidas'),

    # Historias médicas
    path('historias/mascota/<int:mascota_id>/', HistoriasPorMascotaView.as_view(), name='historias_por_mascota'),
    path('historias/veterinario/<int:vet_id>/', HistoriasPorVeterinarioView.as_view(), name='historias_por_veterinario'),
    path('historias/veterinario/<int:vet_id>/mascota/<int:mascota_id>/', HistoriasPorVeterinarioYMascoView.as_view(), name='historias_por_veterinario_mascota'),

    # Vacunas
    path('vacunas/mascota/<int:mascota_id>/', VacunasPorMascotaView.as_view(), name='vacunas_por_mascota'),
    path('vacunas/agregar-directo/', AgregarVacunaDirectaView.as_view(), name='vacuna_directa'),
    path('vacunas/total-por-fecha/<int:mascota_id>/', TotalVacunasPorFechaView.as_view(), name='total_vacunas_por_fecha'),

    # Clínicas
    path('veterinarios-por-clinica/', VeterinariosPorClinicaView.as_view(), name='veterinarios_por_clinica'),
    path('clinicas-disponibles/', ClinicasDisponiblesView.as_view(), name='clinicas_disponibles'),

    # Estadísticas y eventos
    path('mascotas/historial/<int:mascota_id>/', HistorialMascotaView.as_view(), name='historial_mascota'),
    path('mascotas/estadisticas/<int:mascota_id>/', EstadisticasEventosView.as_view(), name='estadisticas_eventos'),
    path('mascotas/consolidado-eventos/<int:mascota_id>/', ConsolidadoEventosMascotaView.as_view(), name='consolidado_eventos'),
    path('mascotas/visitas-veterinario/<int:mascota_id>/', TotalVisitasVeterinarioView.as_view(), name='total_visitas_veterinario'),
    path('mascotas/promedio-recorrido/<int:mascota_id>/', PromedioRecorridoDiarioView.as_view(), name='promedio_recorrido_diario'),

    # Citas
    path('citas/crear/', CrearCitaView.as_view(), name='crear_cita'),
    path('citas/verificar/', VerificarDisponibilidadCitaView.as_view(), name='verificar_cita'),
    path('citas/veterinario/', CitasPorVeterinarioFechaView.as_view(), name='citas_por_fecha'),
    path('citas/<int:cita_id>/estado/', ActualizarEstadoCitaView.as_view(), name='actualizar_estado_cita'),

    # Chats y mensajes
    path('chats/', ListaChatsUsuarioView.as_view(), name='lista_chats_usuario'),  # GET
    path('chats/crear/', CrearChatView.as_view(), name='crear_chat'),              # POST
    path('chats/<int:chat_id>/mensajes/', MensajesPorChatView.as_view(), name='mensajes_por_chat'),  # GET
    path('chats/<int:chat_id>/mensajes/enviar/', EnviarMensajeView.as_view(), name='enviar_mensaje'),  # POST


]
