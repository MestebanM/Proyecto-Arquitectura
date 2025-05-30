# Generated by Django 5.2 on 2025-05-24 04:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_cita'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('usuario1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_iniciados', to=settings.AUTH_USER_MODEL)),
                ('usuario2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_recibidos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
