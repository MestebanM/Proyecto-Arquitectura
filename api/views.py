from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.http import HttpResponse  # ✅ Para la vista de bienvenida
from rest_framework.permissions import AllowAny
from django.db.models.functions import TruncDate
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.db.models import Avg, Count
from django.db.models import Min, Max
from django.utils.dateparse import parse_datetime
from .models import *
from .serializers import *

# -------------------------------
# VISTA DE BIENVENIDA
# -------------------------------
def vista_inicio(request):
    return HttpResponse("<h2>🎉 Bienvenido a la API de PetCare 🐾</h2><p>La API está corriendo correctamente.</p>")

# -------------------------------
# CRUD ViewSets protegidos por token
# -------------------------------

class VeterinariaViewSet(viewsets.ModelViewSet):
    queryset = Veterinaria.objects.all()
    serializer_class = VeterinariaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class MascotaViewSet(viewsets.ModelViewSet):
    serializer_class = MascotaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'cuidador':
            return Mascota.objects.filter(cuidador=user)
        return Mascota.objects.filter(dueño=user)

    def perform_create(self, serializer):
        serializer.save(dueño=self.request.user)

    def perform_update(self, serializer):
        if self.get_object().dueño != self.request.user:
            raise PermissionError("No puedes editar una mascota que no es tuya.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.dueño != self.request.user:
            raise PermissionError("No puedes eliminar esta mascota.")
        instance.delete()

class HistoriaMedicaViewSet(viewsets.ModelViewSet):
    serializer_class = HistoriaMedicaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['mascota', 'veterinario']

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'veterinario':
            return HistoriaMedica.objects.filter(veterinario=user)
        elif user.tipo == 'dueño':
            return HistoriaMedica.objects.filter(mascota__dueño=user)
        return HistoriaMedica.objects.none()

class VacunaViewSet(viewsets.ModelViewSet):
    serializer_class = VacunaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['historia']

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'veterinario':
            return Vacuna.objects.filter(historia__veterinario=user)
        elif user.tipo == 'dueño':
            return Vacuna.objects.filter(historia__mascota__dueño=user)
        elif user.tipo == 'cuidador':
            return Vacuna.objects.filter(historia__mascota__cuidador=user)
        return Vacuna.objects.none()

class RecordatorioViewSet(viewsets.ModelViewSet):
    serializer_class = RecordatorioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['mascota']

    def get_queryset(self):
        usuario = self.request.user
        if usuario.tipo == 'cuidador':
            return Recordatorio.objects.filter(mascota__cuidador=usuario)
        return Recordatorio.objects.filter(mascota__dueño=usuario)

# -------------------------------
# Registro y Login con autenticación real
# -------------------------------

class RegistroUsuarioView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        tipo = request.data.get('tipo')
        tipos_validos = ['dueño', 'veterinario', 'cuidador']

        if tipo not in tipos_validos:
            return Response({'error': f'Tipo inválido. Opciones válidas: {tipos_validos}'}, status=400)

        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            token = Token.objects.create(user=usuario)
            return Response({'token': token.key, 'usuario': serializer.data}, status=201)
        return Response(serializer.errors, status=400)

class LoginUsuarioView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        usuario = authenticate(username=username, password=password)

        if usuario is None:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=usuario)
        return Response({
            'token': token.key,
            'usuario_id': usuario.id,
            'tipo': usuario.tipo,
            'nombre': usuario.username
        }, status=status.HTTP_200_OK)

# -------------------------------
# Vista para actualizar datos del usuario
# -------------------------------

class ActualizarUsuarioView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request):
        user = request.user
        serializer = UsuarioSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Usuario actualizado correctamente.', 'usuario': serializer.data})
        return Response(serializer.errors, status=400)

# -------------------------------
# Vista para que el veterinario consulte todas las historias de una mascota
# -------------------------------

class HistoriasPorMascotaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user
        if user.tipo != 'veterinario':
            return Response({'error': 'Solo los veterinarios pueden acceder a este recurso'}, status=403)

        historias = HistoriaMedica.objects.filter(mascota__id=mascota_id, veterinario=user)
        serializer = HistoriaMedicaSerializer(historias, many=True)
        return Response(serializer.data)

# -------------------------------
# Vista para cambiar la contraseña
# -------------------------------

class CambiarPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request):
        user = request.user
        actual = request.data.get('password_actual')
        nueva = request.data.get('nueva_password')
        confirmar = request.data.get('confirmar_password')

        if not user.check_password(actual):
            return Response({'error': 'La contraseña actual no es correcta'}, status=400)

        if nueva != confirmar:
            return Response({'error': 'La nueva contraseña y la confirmación no coinciden'}, status=400)

        user.set_password(nueva)
        user.save()

        Token.objects.filter(user=user).delete()
        nuevo_token = Token.objects.create(user=user)

        return Response({
            'mensaje': 'Contraseña actualizada exitosamente',
            'nuevo_token': nuevo_token.key
        }, status=200)



class UsuarioConMascotasView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        usuario = request.user

        if usuario.tipo not in ['dueño', 'cuidador']:
            return Response(
                {'error': 'Solo los dueños y cuidadores pueden ver sus mascotas.'},
                status=403
            )

        data_usuario = UsuarioSerializer(usuario).data

        # Obtener mascotas según el tipo
        if usuario.tipo == 'dueño':
            mascotas = Mascota.objects.filter(dueño=usuario)
        else:  # cuidador
            mascotas = Mascota.objects.filter(cuidador=usuario)

        mascotas_data = MascotaSerializer(mascotas, many=True).data

        return Response({
            'usuario': data_usuario,
            'mascotas': mascotas_data
        })



class EliminarCuentaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def delete(self, request):
        user = request.user

        # 1. Eliminar recordatorios de sus mascotas
        if user.tipo == 'dueño':
            for mascota in Mascota.objects.filter(dueño=user):
                mascota.recordatorios.all().delete()
                mascota.historias.all().delete()
                mascota.delete()

        # 2. Si es cuidador, solo desvinculamos (no es dueño de mascotas)
        elif user.tipo == 'cuidador':
            Mascota.objects.filter(cuidador=user).update(cuidador=None)

        # 3. Si es veterinario, eliminamos sus historias y vacunas relacionadas
        elif user.tipo == 'veterinario':
            historias = HistoriaMedica.objects.filter(veterinario=user)
            for historia in historias:
                historia.vacunas.all().delete()
            historias.delete()

        # 4. Eliminar token, luego cuenta
        Token.objects.filter(user=user).delete()
        user.delete()

        return Response({'mensaje': 'Cuenta eliminada correctamente.'}, status=200)

class MascotasAtendidasView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        if user.tipo != 'veterinario':
            return Response({'error': 'Solo los veterinarios pueden acceder a esta información.'}, status=403)

        historias = HistoriaMedica.objects.filter(veterinario=user).select_related('mascota')
        mascotas_unicas = {h.mascota.id: h.mascota for h in historias}

        serializer = MascotaSerializer(mascotas_unicas.values(), many=True)
        return Response(serializer.data, status=200)



class VeterinariosPorClinicaView(APIView):
    permission_classes = [AllowAny]  # 🔓 Ahora es público
    authentication_classes = []      # 🔓 No requiere autenticación

    def get(self, request):
        nombre_clinica = request.query_params.get('clinica')

        if not nombre_clinica:
            return Response({'error': 'Se requiere el parámetro "clinica".'}, status=400)

        veterinaria = Veterinaria.objects.filter(nombre__iexact=nombre_clinica).first()
        if not veterinaria:
            return Response({'error': 'Clínica no encontrada.'}, status=404)

        veterinarios = Usuario.objects.filter(tipo='veterinario', veterinaria=veterinaria)
        data = [
            {
                "id": v.id,
                "nombre_usuario": v.username,
                "email": v.email
            }
            for v in veterinarios
        ]
        return Response(data, status=200)


class ClinicasDisponiblesView(APIView):
    permission_classes = [AllowAny]  # Público
    authentication_classes = []      # Sin autenticación

    def get(self, request):
        clinicas = Veterinaria.objects.filter(
            usuario__tipo='veterinario'
        ).distinct()

        nombres = [c.nombre for c in clinicas]

        return Response(nombres, status=200)
    
 
class VacunasPorMascotaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        # Verificamos si tiene permiso para acceder (dueño o cuidador)
        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user)
        ):
            return Response({'error': 'No tienes permiso para acceder a esta información.'}, status=403)

        # Obtener todas las vacunas relacionadas con las historias médicas de esa mascota
        historias = HistoriaMedica.objects.filter(mascota=mascota)
        vacunas = Vacuna.objects.filter(historia__in=historias)

        serializer = VacunaSerializer(vacunas, many=True)
        return Response(serializer.data, status=200)


class AgregarVacunaDirectaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user
        if user.tipo != 'veterinario':
            return Response({'error': 'Solo los veterinarios pueden agregar vacunas.'}, status=403)

        mascota_id = request.data.get('mascota')
        nombre_vacuna = request.data.get('nombre')
        fecha = request.data.get('fecha')
        descripcion_historia = request.data.get('descripcion', 'Atención general')

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        historia = HistoriaMedica.objects.create(
            mascota=mascota,
            veterinario=user,
            descripcion=descripcion_historia
        )

        vacuna = Vacuna.objects.create(
            historia=historia,
            nombre=nombre_vacuna,
            fecha=fecha
        )

        return Response({
            'mensaje': 'Vacuna y historia médica registradas correctamente.',
            'vacuna_id': vacuna.id
        }, status=201)


class ActualizarMascotaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request, mascota_id):
        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        user = request.user
        if mascota.dueño != user and mascota.cuidador != user:
            return Response({'error': 'No tienes permisos para editar esta mascota.'}, status=403)

        serializer = MascotaSerializer(mascota, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Mascota actualizada correctamente.', 'mascota': serializer.data})
        return Response(serializer.errors, status=400)
    
class AdministrarUsuariosView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'error': 'Acceso denegado. Solo para superusuarios.'}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({'mensaje': 'Usuario creado correctamente', 'usuario': UsuarioSerializer(usuario).data}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, user_id):
        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Usuario actualizado', 'usuario': serializer.data})
        return Response(serializer.errors, status=400)
    
    def delete(self, request, user_id):
        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        usuario.delete()
        return Response(
            {'mensaje': 'Usuario eliminado correctamente'},
            status=200,
            content_type='application/json'
        )

class MascotasPorUsuarioView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, usuario_id):
        usuario = request.user

        if not usuario.is_superuser and usuario.tipo != 'veterinario':
            return Response({'error': 'Acceso denegado. Solo superusuarios o veterinarios pueden acceder.'}, status=403)

        try:
            dueño = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        mascotas = Mascota.objects.filter(dueño=dueño)
        serializer = MascotaSerializer(mascotas, many=True)
        return Response(serializer.data, status=200)
    
class EventoMascotaViewSet(viewsets.ModelViewSet):
    serializer_class = EventoMascotaSerializer
    queryset = EventoMascota.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['mascota', 'tipo']

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'cuidador':
            return EventoMascota.objects.filter(mascota__cuidador=user)
        return EventoMascota.objects.filter(mascota__dueño=user)

    def perform_create(self, serializer):
        mascota = serializer.validated_data['mascota']
        user = self.request.user
        if mascota.dueño != user and mascota.cuidador != user:
            raise PermissionError("No puedes registrar eventos para esta mascota.")
        serializer.save()

    def perform_update(self, serializer):
        evento = self.get_object()
        user = self.request.user
        if evento.mascota.dueño != user and evento.mascota.cuidador != user:
            raise PermissionError("No puedes editar este evento.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.mascota.dueño != user and instance.mascota.cuidador != user:
            raise PermissionError("No puedes eliminar este evento.")
        instance.delete()


class HistorialMascotaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        # Verificamos permisos
        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user)
        ):
            return Response({'error': 'No tienes permiso para ver el historial de esta mascota.'}, status=403)

        eventos = EventoMascota.objects.filter(mascota=mascota).order_by('-fecha')
        serializer = EventoMascotaSerializer(eventos, many=True)

        return Response({
            "mascota": mascota.nombre,
            "historial": serializer.data
        }, status=200)


class EstadisticasEventosView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user)
        ):
            return Response({'error': 'No tienes permiso para ver estas estadísticas.'}, status=403)

        # Filtro por fechas opcional
        fecha_inicio = request.query_params.get('inicio')
        fecha_fin = request.query_params.get('fin')

        eventos = EventoMascota.objects.filter(mascota=mascota)

        if fecha_inicio:
            eventos = eventos.filter(fecha__gte=parse_datetime(fecha_inicio))
        if fecha_fin:
            eventos = eventos.filter(fecha__lte=parse_datetime(fecha_fin))

        total = eventos.count()
        promedio_duracion = eventos.aggregate(promedio=Avg('duracion_min'))['promedio']

        return Response({
            "mascota": mascota.nombre,
            "total_eventos": total,
            "promedio_duracion_minutos": round(promedio_duracion or 0, 2)
        }, status=200)
    
class RecorridoMascotaViewSet(viewsets.ModelViewSet):
    serializer_class = RecorridoMascotaSerializer
    queryset = RecorridoMascota.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['mascota']

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'cuidador':
            return RecorridoMascota.objects.filter(mascota__cuidador=user)
        return RecorridoMascota.objects.filter(mascota__dueño=user)

    def perform_create(self, serializer):
        mascota = serializer.validated_data['mascota']
        user = self.request.user
        if mascota.dueño != user and mascota.cuidador != user:
            raise PermissionError("No puedes registrar recorridos para esta mascota.")
        serializer.save()

    def perform_update(self, serializer):
        recorrido = self.get_object()
        user = self.request.user
        if recorrido.mascota.dueño != user and recorrido.mascota.cuidador != user:
            raise PermissionError("No puedes editar este recorrido.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.mascota.dueño != user and instance.mascota.cuidador != user:
            raise PermissionError("No puedes eliminar este recorrido.")
        instance.delete()


class TotalVacunasPorFechaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user) or
            user.tipo == 'veterinario'
        ):
            return Response({'error': 'No tienes permiso para ver las vacunas de esta mascota.'}, status=403)

        fecha_inicio = request.query_params.get('inicio')
        fecha_fin = request.query_params.get('fin')

        vacunas = Vacuna.objects.filter(historia__mascota=mascota)

        # Calculamos el rango real si no se envían filtros
        if not fecha_inicio and not fecha_fin:
            fechas = vacunas.aggregate(
                fecha_min=Min('fecha'),
                fecha_max=Max('fecha')
            )
            fecha_inicio = fechas['fecha_min']
            fecha_fin = fechas['fecha_max']
        else:
            if fecha_inicio:
                vacunas = vacunas.filter(fecha__gte=parse_date(fecha_inicio))
            if fecha_fin:
                vacunas = vacunas.filter(fecha__lte=parse_date(fecha_fin))

        total = vacunas.count()

        return Response({
            "mascota": mascota.nombre,
            "total_vacunas": total,
            "filtro_fecha_inicio": str(fecha_inicio) if fecha_inicio else None,
            "filtro_fecha_fin": str(fecha_fin) if fecha_fin else None
        }, status=200)



class TotalVisitasVeterinarioView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user) or
            user.tipo == 'veterinario'
        ):
            return Response({'error': 'No tienes permiso para ver esta información.'}, status=403)

        total_visitas = HistoriaMedica.objects.filter(mascota=mascota).count()

        return Response({
            "mascota": mascota.nombre,
            "total_visitas_veterinario": total_visitas
        }, status=200)


class ConsolidadoEventosMascotaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user)
        ):
            return Response({'error': 'No tienes permiso para ver esta información.'}, status=403)

        eventos_agrupados = EventoMascota.objects.filter(mascota=mascota)\
            .values('tipo')\
            .annotate(total=Count('id'))\
            .order_by('-total')

        return Response({
            "mascota": mascota.nombre,
            "consolidado_eventos": eventos_agrupados
        }, status=200)
    


class PromedioRecorridoDiarioView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, mascota_id):
        user = request.user

        try:
            mascota = Mascota.objects.get(id=mascota_id)
        except Mascota.DoesNotExist:
            return Response({'error': 'Mascota no encontrada.'}, status=404)

        if not (
            (user.tipo == 'dueño' and mascota.dueño == user) or
            (user.tipo == 'cuidador' and mascota.cuidador == user)
        ):
            return Response({'error': 'No tienes permiso para ver esta información.'}, status=403)

        # Agrupar recorridos por fecha y sumar distancia por día
        recorridos_agrupados = RecorridoMascota.objects.filter(mascota=mascota)\
            .annotate(dia=TruncDate('fecha'))\
            .values('dia')\
            .annotate(distancia_total_dia=Sum('distancia_metros'))\
            .order_by('dia')

        total_dias = recorridos_agrupados.count()
        total_distancia = sum(r['distancia_total_dia'] for r in recorridos_agrupados)

        promedio = round(total_distancia / total_dias, 2) if total_dias > 0 else 0

        return Response({
            "mascota": mascota.nombre,
            "total_dias_con_registro": total_dias,
            "total_distancia_metros": total_distancia,
            "promedio_diario_metros": promedio
        }, status=200)