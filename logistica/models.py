from django.db import models
from django.contrib.auth.models import Group, User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, unique=True)

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
    
class PontoAtendimentoInfo(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='informacoes')
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    limite = models.IntegerField(verbose_name="Limite de bipagens", default=50)
    liberado = models.BooleanField(default=False, verbose_name="Acesso liberado")

    def __str__(self):
        return f"{self.group.name} - {self.endereco}"

class GroupAditionalInformation(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='informacoes_adicionais')
    logradouro = models.CharField(max_length=255, verbose_name="Logradouro", blank=True, null=True)
    numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    complemento = models.CharField(max_length=100, verbose_name="Complemento", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    UF = models.CharField(max_length=2, verbose_name="Estado", blank=True, null=True)
    CEP = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    estado = models.CharField(max_length=2, verbose_name="Estado", blank=True, null=True)
    telefone1 = models.CharField(max_length=15, verbose_name="Telefone 1", blank=True, null=True)
    telefone2 = models.CharField(max_length=15, verbose_name="Telefone 2", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    responsavel = models.CharField(max_length=100, verbose_name="Responsável", blank=True, null=True)

    def __str__(self):
        return f"{self.group.name} - Contato"

class PermissaoUsuarioDummy(models.Model):
    class Meta:
        verbose_name = "Transporte | Permissão de Usuario"
        verbose_name_plural = "Transporte | Permissões de Usuários"
        permissions = [
            ("pode_gerenciar_usuarios", "Pode gerenciar usuários"),
            ("pode_gerenciar_grupos", "Pode gerenciar grupos"),
            ("usuario_credenciado", "Usuário credenciado"),
        ]
    def __str__(self):
        return "Permissões personalizadas"