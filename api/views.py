from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate  # 🔥 IMPORTANTE

from .models import *
from .serializers import *

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

        # Cambiar la contraseña
        user.set_password(nueva)
        user.save()

        # Eliminar el token anterior
        Token.objects.filter(user=user).delete()

        # Crear nuevo token
        nuevo_token = Token.objects.create(user=user)

        return Response({
            'mensaje': 'Contraseña actualizada exitosamente',
            'nuevo_token': nuevo_token.key
        }, status=200)
