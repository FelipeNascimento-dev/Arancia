from django.db import models
from django.contrib.auth.models import User, Group


def user_avatar_path(instance, filename):
    return f"avatars/user_{instance.user_id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil")
    cpf = models.CharField(max_length=14, unique=True,
                           blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path, blank=True, null=True)

    def avatar_url(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                pass
        return "/static/global/images/default-avatar.png"


class Romaneio(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    codigo_rastreio = models.CharField(max_length=20, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Romaneio {self.numero}'


class ItemRomaneio(models.Model):
    romaneio = models.ForeignKey(
        Romaneio, on_delete=models.CASCADE, related_name='itens')
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
    group = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name='informacoes')
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    limite = models.IntegerField(verbose_name="Limite de bipagens", default=50)
    liberado = models.BooleanField(
        default=False, verbose_name="Acesso liberado")

    def __str__(self):
        return f"{self.group.name} - {self.endereco}"


class GroupAditionalInformation(models.Model):
    group = models.ForeignKey(Group, related_name='informacoes_adicionais',
                              blank=True, null=True, on_delete=models.CASCADE)
    nome = models.CharField(
        max_length=100, verbose_name="Nome", blank=True, null=True)
    cod_iata = models.CharField(
        max_length=100, verbose_name="Código IATA", blank=True, null=True)
    sales_channel = models.CharField(
        max_length=100, verbose_name="Sales Channel", blank=True, null=True)
    deposito = models.CharField(
        max_length=100, verbose_name="Depósito", blank=True, null=True)
    logradouro = models.CharField(
        max_length=255, verbose_name="Logradouro", blank=True, null=True)
    numero = models.CharField(
        max_length=10, verbose_name="Número", blank=True, null=True)
    complemento = models.CharField(
        max_length=100, verbose_name="Complemento", blank=True, null=True)
    bairro = models.CharField(
        max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(
        max_length=100, verbose_name="Cidade", blank=True, null=True)
    UF = models.CharField(
        max_length=2, verbose_name="Estado", blank=True, null=True)
    CEP = models.CharField(
        max_length=10, verbose_name="CEP", blank=True, null=True)
    estado = models.CharField(
        max_length=2, verbose_name="Estado", blank=True, null=True)
    telefone1 = models.CharField(
        max_length=15, verbose_name="Telefone 1", blank=True, null=True)
    telefone2 = models.CharField(
        max_length=15, verbose_name="Telefone 2", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    responsavel = models.CharField(
        max_length=100, verbose_name="Responsável", blank=True, null=True)

    def __str__(self):
        return f"{self.group.name}" if self.group else "Sem grupo"


class UserDesignation(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='designacao')
    informacao_adicional = models.ForeignKey(
        GroupAditionalInformation, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.informacao_adicional}"


class PermissaoUsuarioDummy(models.Model):
    class Meta:
        verbose_name = "--Personalizada--"
        verbose_name_plural = "--Personalizadas--"
        permissions = [
            ("lastmile_b2c", "LastMile (B2C)"),
            ("entrada_flfm", "Entrada (Fulfillment)"),
        ]

    def __str__(self):
        return "Permissões personalizadas"
