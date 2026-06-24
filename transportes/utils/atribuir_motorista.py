from django.db.models import Q
from django.db.models.functions import Lower

from logistica.models import GroupAditionalInformation


def _listar_pa_opcoes():
    pa_qs = (
        GroupAditionalInformation.objects
        .filter(
            Q(group__name="arancia_PA") |
            Q(group__name="arancia_TRANSPORT", nome="C-TRENDS")
        )
        .annotate(nome_lower=Lower("nome"))
        .order_by("nome_lower")
        .values_list("id", "nome")
        .distinct()
    )
    return [(str(pa_id), nome) for pa_id, nome in pa_qs]


def obter_contexto_atribuir_motorista(user):
    usuario_eh_arancia_pa = user.groups.filter(name="arancia_PA").exists()
    # Transportadora é filtro opcional e independente da PA; usuário PA não precisa informá-la.
    pode_escolher_transportadora = not usuario_eh_arancia_pa

    user_designation = getattr(
        getattr(user, "designacao", None), "informacao_adicional", None
    )
    user_designation_id = ""
    user_designation_nome = ""

    if user_designation is not None:
        user_designation_id = str(
            getattr(user_designation, "id", "") or ""
        ).strip()
        user_designation_nome = str(
            getattr(user_designation, "nome", "") or ""
        ).strip()

    if usuario_eh_arancia_pa and user_designation_id:
        pa_opcoes = [
            (user_designation_id, user_designation_nome or user_designation_id)
        ]
        pa_travada = True
        pa_padrao_id = user_designation_id
        pa_padrao_nome = user_designation_nome
    else:
        pa_opcoes = _listar_pa_opcoes()
        pa_travada = False
        pa_padrao_id = ""
        pa_padrao_nome = ""

    return {
        "usuario_eh_arancia_pa": usuario_eh_arancia_pa,
        "pode_escolher_transportadora": pode_escolher_transportadora,
        "pa_opcoes": pa_opcoes,
        "pa_travada": pa_travada,
        "pa_padrao_id": pa_padrao_id,
        "pa_padrao_nome": pa_padrao_nome,
        "user_designation_id": user_designation_id,
        "user_designation_nome": user_designation_nome,
    }


def validar_pa_atribuir_motorista(user, pa_id):
    ctx = obter_contexto_atribuir_motorista(user)
    pa_id = str(pa_id or "").strip()

    if ctx["pa_travada"]:
        expected = ctx["pa_padrao_id"]
        if pa_id and pa_id != expected:
            return False, "Você só pode atribuir motorista para a sua própria PA.", expected
        if not expected:
            return False, "Usuário PA sem designação válida configurada.", ""
        return True, "", expected

    if not pa_id:
        return False, "Selecione uma PA.", ""

    valid_ids = {str(p[0]) for p in ctx["pa_opcoes"]}
    if pa_id not in valid_ids:
        return False, "PA selecionada inválida.", ""

    return True, "", pa_id


def validar_gai_id_busca_motorista(user, gai_id):
    ok, _, pa_id = validar_pa_atribuir_motorista(user, gai_id)
    if not ok:
        return False, "", "PA inválida para busca de motorista."
    return True, pa_id, ""


def montar_url_atualizar_motorista(created_by, carrier_id=""):
    from setup.local_settings import TRANSP_API_URL

    url = (
        f"{TRANSP_API_URL}/v2/order_travel/driver/updated"
        f"?created_by={created_by}"
    )
    carrier_id = str(carrier_id or "").strip()
    if carrier_id:
        url += f"&carrier_id={carrier_id}"
    return url
