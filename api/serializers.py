from rest_framework import serializers
from .models import *

class VeterinariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinaria
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'tipo', 'veterinaria']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            tipo=validated_data.get('tipo'),
            veterinaria=validated_data.get('veterinaria')
        )
        return user


class MascotaSerializer(serializers.ModelSerializer):
    nombre_dueño = serializers.CharField(source='dueño.username', read_only=True)
    nombre_cuidador = serializers.CharField(source='cuidador.username', read_only=True)

    class Meta:
        model = Mascota
        fields = ['id', 'nombre', 'especie', 'dueño', 'cuidador', 'nombre_dueño', 'nombre_cuidador']


class HistoriaMedicaSerializer(serializers.ModelSerializer):
    nombre_veterinario = serializers.CharField(source='veterinario.username', read_only=True)
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)

    class Meta:
        model = HistoriaMedica
        fields = ['id', 'mascota', 'veterinario', 'descripcion', 'fecha', 'nombre_veterinario', 'nombre_mascota']


class VacunaSerializer(serializers.ModelSerializer):
    nombre_historia = serializers.CharField(source='historia.descripcion', read_only=True)
    nombre_mascota = serializers.CharField(source='historia.mascota.nombre', read_only=True)

    class Meta:
        model = Vacuna
        fields = ['id', 'historia', 'nombre', 'fecha', 'nombre_historia', 'nombre_mascota']


class RecordatorioSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)

    class Meta:
        model = Recordatorio
        fields = ['id', 'mascota', 'mensaje', 'fecha', 'nombre_mascota']

class EventoMascotaSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)

    class Meta:
        model = EventoMascota
        fields = ['id', 'mascota', 'tipo', 'descripcion', 'fecha', 'duracion_min', 'nombre_mascota']

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    usuario1 = UsuarioSerializer(read_only=True)
    usuario2 = UsuarioSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'usuario1', 'usuario2', 'creado']

class MensajeSerializer(serializers.ModelSerializer):
    emisor_username = serializers.CharField(source='emisor.username', read_only=True)
    fecha_envio = serializers.DateTimeField(source='enviado_en', read_only=True)

    class Meta:
        model = Mensaje
        fields = ['id', 'chat', 'emisor', 'emisor_username', 'contenido', 'fecha_envio']

class RecorridoMascotaSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)

    class Meta:
        model = RecorridoMascota
        fields = ['id', 'mascota', 'distancia_metros', 'duracion_minutos', 'fecha', 'notas', 'nombre_mascota']

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Direccion
        fields = '__all__'
        read_only_fields = ('usuario', 'creado_en')


class HorarioNoDisponibleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HorarioNoDisponible
        fields = '__all__'
        read_only_fields = ('veterinario',)


class ControlFisicoSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)

    class Meta:
        model  = ControlFisico
        fields = ['id', 'mascota', 'fecha', 'peso', 'talla', 'nombre_mascota']


class HistorialServicioSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)
    nombre_cuidador = serializers.CharField(source='cuidador.username', read_only=True)

    class Meta:
        model  = HistorialServicio
        fields = ['id', 'mascota', 'cuidador', 'tipo', 'comentario', 'fecha',
                  'nombre_mascota', 'nombre_cuidador']


class PaseoProgramadoSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)

    class Meta:
        model  = PaseoProgramado
        fields = ['id', 'mascota', 'nombre', 'latitudes', 'longitudes', 'creado_en',
                  'nombre_mascota']