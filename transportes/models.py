import httpx
from datetime import datetime
from setup.local_settings import status_labels, TOKEN, API_BASE
from django.db import models
from django.conf import settings


def auth_headers():
    return {"accept": "application/json", "access_token": TOKEN}


async def fetch_json(url: str, default=None):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers=auth_headers())
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"[ERRO] GET {url}: {e}")
        return default if default is not None else {}


def sum_counts(counts: dict) -> int:
    return sum(int(counts.get(k, 0) or 0) for k in status_labels.keys())


def initials(nome: str) -> str:
    parts = (nome or "").strip().split()
    if not parts:
        return "T"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def now_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class UsuarioExtra(models.Model):
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    cod_base = models.CharField(max_length=50)
    nome_unidade = models.CharField(max_length=100, blank=True, null=True)
    documento = models.CharField(max_length=50)
    profile = models.CharField(max_length=100, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class PersonalPermissions(models.Model):
    class Meta:
        verbose_name = "--Transp-Permission--"
        verbose_name_plural = "--Transp-Permissions--"
        permissions = [
            ("controle_campo", "Controle de Campo"),
            ("gerar_etiquetas", "Gerar Etiquetas"),
            ("transp_menu", "Mostrar menu transporte"),
            ("CC_admin", "Mostrar menu administrativo"),
            ("CC_gerencial", "Controle de campo gerencial"),
            ("controle_chamados", "Controle de Chamados"),
            ("transportes", "Permissão total para transporte"),
        ]

    def __str__(self):
        return "Personal Permissions"


class FiltroFavoritoUsuario(models.Model):
    TELA_CONSULTA_OS = "consulta_os_transp"
    TELA_LISTA_VIAGENS = "lista_viagens"

    CHOICES_TELA = [
        (TELA_CONSULTA_OS, "Consulta OS"),
        (TELA_LISTA_VIAGENS, "Lista de Viagens"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="filtros_favoritos"
    )
    chave_tela = models.CharField(max_length=100, choices=CHOICES_TELA)
    nome = models.CharField(max_length=100, default="Meu filtro favorito")
    filtros = models.JSONField(default=dict, blank=True)
    favorito = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Filtro favorito do usuário"
        verbose_name_plural = "Filtros favoritos dos usuários"
        unique_together = ("usuario", "chave_tela", "nome")

    def __str__(self):
        return f"{self.usuario} - {self.chave_tela} - {self.nome}"


class FiltroPadraoTela(models.Model):
    chave_tela = models.CharField(max_length=100, unique=True)
    nome = models.CharField(max_length=100, default="Padrão do sistema")
    filtros = models.JSONField(default=dict, blank=True)
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Filtro padrão da tela"
        verbose_name_plural = "Filtros padrão das telas"

    def __str__(self):
        return f"{self.chave_tela} - {self.nome}"
