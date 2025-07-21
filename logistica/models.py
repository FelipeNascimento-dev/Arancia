from django.db import models

class Romaneio(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    codigo_rastreio = models.CharField(max_length=20, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Romaneio {self.numero}'
    

class ItemRomaneio(models.Model):
    romaneio = models.ForeignKey(Romaneio, on_delete=models.CASCADE, related_name='itens')
    serial = models.CharField(max_length=100)
    chamado = models.CharField(max_length=100)
    data = models.CharField(max_length=10)
    hora = models.CharField(max_length=10)
    usuario = models.CharField(max_length=100)
    filial = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)

    def __str__(self):
        return f'Serial {self.serial} do {self.romaneio.numero}'