from django.db import models
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
