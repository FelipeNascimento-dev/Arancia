from django.db import models
from django.contrib.auth.models import User, Group
from datetime import timedelta
from django.conf import settings
from django.utils import timezone


def user_avatar_path(instance, filename):
    return f"avatars/user_{instance.user_id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil")
    cpf = models.CharField(max_length=14, unique=True,
                           blank=True, null=True)
    avatar = models.URLField(
        blank=True, null=True)


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


class RomaneioReverse(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Romaneio {self.numero}"


class GroupAditionalInformation(models.Model):
    group = models.ForeignKey(Group, related_name='informacoes_adicionais',
                              blank=True, null=True, on_delete=models.CASCADE)
    razao_social = models.CharField(
        max_length=100, verbose_name="Razão Social", blank=True, null=True)
    nome = models.CharField(
        max_length=100, verbose_name="Nome", blank=True, null=True)
    cod_iata = models.CharField(
        max_length=100, verbose_name="Código IATA", blank=True, null=True)
    sales_channel = models.CharField(
        max_length=100, verbose_name="Sales Channel", blank=True, null=True)
    cod_center = models.CharField(
        verbose_name="Centro de Custos", blank=True, null=True)
    deposito = models.CharField(
        max_length=100, verbose_name="Depósito", blank=True, null=True)
    cnpj = models.CharField(
        max_length=100, verbose_name="CNPJ", blank=True, null=True)
    inscricao_estadual = models.CharField(
        max_length=50, verbose_name="Inscrição Estadual", blank=True, null=True)
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
    codigo_ibge = models.CharField(
        max_length=100, verbose_name="Código IBGE", blank=True, null=True)
    telefone1 = models.CharField(
        max_length=15, verbose_name="Telefone 1", blank=True, null=True)
    telefone2 = models.CharField(
        max_length=15, verbose_name="Telefone 2", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    responsavel = models.CharField(
        max_length=100, verbose_name="Responsável", blank=True, null=True)

    def __str__(self):
        return f"{self.cod_iata}-{self.nome}" if self.group else "Sem grupo"


class GroupAditionalInformationLegacy(models.Model):
    id = models.AutoField(primary_key=True)
    gaiid = models.ForeignKey(
        GroupAditionalInformation,
        on_delete=models.CASCADE,
        related_name="legacy_entries",
        verbose_name="GAI (GroupAditionalInformation)"
    )
    cod_contato = models.CharField(
        max_length=100, verbose_name="Código do Contato")

    def __str__(self):
        return f"Legacy {self.gaiid} - {self.cod_contato}"


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
            ("acesso_arancia", "Acesso Arancia"),
            ("ti_interno", "TI Interno"),
            ("logistica_perm", "Permissão Logistica"),
            ("lastmile_b2c", "LastMile (B2C)"),
            ("entrada_flfm", "Entrada (Fulfillment)"),
            ("pode_gerenciar_filiais", "Pode Gerenciar Filiais"),
            ("gestao_total", "Gestão Total"),
            ("inst_simplified", "Instalação Simplificada"),
            ("entrega_com_sap", "Entrega com SAP"),
            ("checkin_principal", "Check-in Principal"),
            ("checkout_principal", "Check-out Principal"),
            ("products_management", "Gerenciamento de Produtos"),
            ("estoque", "Pode Visualizar Estoque"),
            ("gerente_estoque", "Gerente de Estoque"),
            ("reverse", "Reversa"),
            ("desinstalacao", "Pode fazer Desinstalação")
        ]

    def __str__(self):
        return "Permissões personalizadas"


# SENHAS
class UserPasswordControl(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_control"
    )
    password_changed_at = models.DateTimeField(default=timezone.now)
    force_change_password = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Controle de senha"
        verbose_name_plural = "Controles de senha"

    def expire_at(self):
        expiration_days = getattr(settings, "PASSWORD_EXPIRATION_DAYS", 30)
        return self.password_changed_at + timedelta(days=expiration_days)

    def days_to_expire(self):
        remaining = self.expire_at().date() - timezone.localdate()
        return max(0, remaining.days)

    def is_password_expired(self):
        return self.force_change_password or timezone.now() >= self.expire_at()

    def should_warn(self):
        warning_days = getattr(settings, "PASSWORD_WARNING_DAYS", 7)
        return not self.is_password_expired() and self.days_to_expire() <= warning_days

    def mark_password_changed(self):
        self.password_changed_at = timezone.now()
        self.force_change_password = False
        self.save(update_fields=[
                  "password_changed_at", "force_change_password"])


class PasswordResetAccessCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reset_access_codes"
    )
    code_hash = models.CharField(max_length=255)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Código único de acesso"
        verbose_name_plural = "Códigos únicos de acesso"

    def is_expired(self):
        minutes = getattr(
            settings, "PASSWORD_RESET_CODE_EXPIRATION_MINUTES", 15)
        return timezone.now() > self.created_at + timedelta(minutes=minutes)

    def is_valid(self):
        return not self.used and not self.is_expired()
