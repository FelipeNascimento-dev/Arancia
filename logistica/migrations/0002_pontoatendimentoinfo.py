# Generated by Django 5.2.1 on 2025-07-29 20:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('logistica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PontoAtendimentoInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endereco', models.CharField(max_length=255, verbose_name='Endereço')),
                ('limite', models.IntegerField(default=50, verbose_name='Limite de bipagens')),
                ('liberado', models.BooleanField(default=False, verbose_name='Acesso liberado')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='informacoes', to='auth.group')),
            ],
        ),
    ]
