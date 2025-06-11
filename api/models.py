from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Veterinaria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('dueño', 'Dueño'),
        ('veterinario', 'Veterinario'),
        ('cuidador', 'Cuidador'),
    ]

    email = models.EmailField(unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, blank=True, null=True)
    veterinaria = models.ForeignKey(Veterinaria, null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} - {self.tipo if self.tipo else 'N/A'}"


class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    dueño = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mascotas')
    cuidador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='mascotas_cuidador')

    def __str__(self):
        return self.nombre


class HistoriaMedica(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historias')
    veterinario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historias_veterinario')
    descripcion = models.TextField()
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Historia de {self.mascota.nombre} - {self.fecha}"


class Cita(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas')
    dueño = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas_dueño')
    veterinario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas_veterinario')
    fecha = models.DateField()
    hora = models.TimeField()
    historia = models.ForeignKey(HistoriaMedica, on_delete=models.CASCADE, related_name='citas')
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('realizada', 'Realizada'),
            ('cancelada', 'Cancelada')
        ],
        default='pendiente'
    )

    def __str__(self):
        return f"Cita para {self.mascota.nombre} el {self.fecha} a las {self.hora}"


class Vacuna(models.Model):
    historia = models.ForeignKey(HistoriaMedica, on_delete=models.CASCADE, related_name='vacunas')
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"


class Recordatorio(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='recordatorios')
    mensaje = models.CharField(max_length=200)
    fecha = models.DateTimeField()

    def __str__(self):
        return f"Recordatorio para {self.mascota.nombre} el {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class EventoMascota(models.Model):
    TIPO_EVENTO = [
        ('paseo', 'Paseo'),
        ('alimentacion', 'Alimentación'),
        ('juego', 'Juego'),
        ('baño', 'Baño'),
        ('vacuna', 'Vacuna'),
        ('otro', 'Otro'),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='eventos')
    tipo = models.CharField(max_length=20, choices=TIPO_EVENTO)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    duracion_min = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.mascota.nombre} ({self.fecha.strftime('%Y-%m-%d %H:%M')})"

class Chat(models.Model):
    usuario1 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='chats_iniciados')
    usuario2 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='chats_recibidos')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat entre {self.usuario1.username} y {self.usuario2.username}"


class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='mensajes')
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contenido = models.TextField()
    enviado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emisor.username}: {self.contenido[:30]}"


class RecorridoMascota(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='recorridos')
    distancia_metros = models.PositiveIntegerField()
    duracion_minutos = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.distancia_metros} m - {self.fecha.strftime('%Y-%m-%d')}"

class Direccion(models.Model):
    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='direcciones')
    nombre     = models.CharField(max_length=80)
    direccion  = models.CharField(max_length=150)
    latitud    = models.FloatField()
    longitud   = models.FloatField()
    creado_en  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.usuario.username})"


class HorarioNoDisponible(models.Model):
    veterinario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    limit_choices_to={'tipo': 'veterinario'},
                                    related_name='horarios_no_disponibles')
    fecha       = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()

    class Meta:
        unique_together = ('veterinario', 'fecha', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f"{self.veterinario.username} {self.fecha} {self.hora_inicio}-{self.hora_fin}"


class ControlFisico(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='controles_fisicos')
    fecha   = models.DateField()                # se usa como “id natural”
    peso    = models.CharField(max_length=15)   # p. ej. 4.5 kg
    talla   = models.CharField(max_length=15)   # p. ej. 35 cm

    class Meta:
        unique_together = ('mascota', 'fecha')

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha}"


class HistorialServicio(models.Model):
    mascota     = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historial_servicios')
    cuidador    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    limit_choices_to={'tipo': 'cuidador'},
                                    related_name='servicios_realizados')
    tipo        = models.CharField(max_length=30)          # libre: paseo, baño, etc.
    comentario  = models.TextField(blank=True)
    fecha       = models.DateField()
    creado_en   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.mascota.nombre} ({self.fecha})"


class PaseoProgramado(models.Model):
    mascota     = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='paseos_programados')
    nombre      = models.CharField(max_length=80)
    latitudes   = models.JSONField()   # lista de floats
    longitudes  = models.JSONField()
    creado_en   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.mascota.nombre})"