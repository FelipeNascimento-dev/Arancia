# Generated by Django 5.2.1 on 2025-07-30 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0005_rename_permissoes_permition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupaditionalinformation',
            name='endereco',
        ),
        migrations.AddField(
            model_name='groupaditionalinformation',
            name='UF',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='groupaditionalinformation',
            name='bairro',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Bairro'),
        ),
        migrations.AddField(
            model_name='groupaditionalinformation',
            name='complemento',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Complemento'),
        ),
        migrations.AddField(
            model_name='groupaditionalinformation',
            name='logradouro',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Logradouro'),
        ),
        migrations.AddField(
            model_name='groupaditionalinformation',
            name='numero',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Número'),
        ),
    ]
