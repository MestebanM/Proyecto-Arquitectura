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
