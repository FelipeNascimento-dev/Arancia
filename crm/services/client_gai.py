from django.contrib.auth.models import Group
from django.db import transaction

from logistica.models import GroupAditionalInformation

CLIENT_GAI_GROUP_NAMES = ("arancia_client", "arancia_CUSTOMER")

GAI_FIELD_NAMES = (
    "razao_social",
    "nome",
    "responsavel",
    "cod_iata",
    "sales_channel",
    "cod_center",
    "deposito",
    "cnpj",
    "inscricao_estadual",
    "CEP",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "UF",
    "codigo_ibge",
    "telefone1",
    "telefone2",
    "email",
)


class ClientGaiGroupNotConfigured(Exception):
    """Grupo Django para clientes CRM não encontrado."""


def get_client_gai_group():
    for name in CLIENT_GAI_GROUP_NAMES:
        group = Group.objects.filter(name=name).first()
        if group:
            return group
    raise ClientGaiGroupNotConfigured(
        "Configure o grupo Django arancia_client ou arancia_CUSTOMER."
    )


def _extract_gai_fields(cleaned_data):
    return {
        key: cleaned_data[key]
        for key in GAI_FIELD_NAMES
        if key in cleaned_data and cleaned_data[key] not in (None, "")
    }


def build_crm_client_payload(cleaned_data, gai_id):
    payload = {
        "gai_id": gai_id,
        "nome": cleaned_data.get("nome"),
        "razao_social": cleaned_data.get("razao_social"),
        "cnpj": cleaned_data.get("cnpj"),
        "email": cleaned_data.get("email"),
        "telefone": cleaned_data.get("telefone1"),
        "sales_channel": cleaned_data.get("sales_channel"),
        "cod_iata": cleaned_data.get("cod_iata"),
        "notes": cleaned_data.get("notes"),
    }
    return {k: v for k, v in payload.items() if v not in (None, "")}


def create_client_with_gai(cleaned_data, *, register_in_api):
    """
    Cria GAI no grupo de clientes e registra o cliente na API CRM.

    ``register_in_api`` deve ser um callable que recebe o payload CRM.
    """
    group = get_client_gai_group()
    gai_fields = _extract_gai_fields(cleaned_data)

    with transaction.atomic():
        gai = GroupAditionalInformation.objects.create(group=group, **gai_fields)
        api_result = register_in_api(build_crm_client_payload(cleaned_data, gai.id))

    return gai, api_result
