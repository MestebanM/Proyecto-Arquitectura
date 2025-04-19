from django.contrib import admin
from django.urls import path, include
from api.views import vista_inicio  # 👈 importa la vista de bienvenida

urlpatterns = [
    path('', vista_inicio),  # 👈 aquí se muestra el texto por defecto al entrar a /
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # 👈 mantiene tus rutas de la app API
]
