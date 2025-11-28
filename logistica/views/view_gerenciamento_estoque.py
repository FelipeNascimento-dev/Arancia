from ..forms import GerenciamentoEstoqueForm
from django.shortcuts import render
from django.contrib import messages
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
import json
from ..models import GroupAditionalInformation

JSON_CT = "application/json"


def gerenciamento_estoque(request):
    titulo = "Gerenciamento de Estoque"
    user = request.user
    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=1000"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        data = result if isinstance(
            result, (dict, list)) else json.loads(result)

        client_choices = [
            (str(i.get("client_code", "")), i.get("client_name", "Sem nome"))
            for i in data
        ] if isinstance(data, list) else []

    except Exception as e:
        messages.error(request, f"Erro ao obter clientes: {e}")
        client_choices = []

    user_cd = getattr(user.designacao, "informacao_adicional", None)

    if user.has_perm("logistica.gerente_estoque"):
        cd_queryset = GroupAditionalInformation.objects.filter(
            group__name__icontains="arancia_pa"
        )

        cd_choices = [
            (g.id, f"{g.cod_iata} - {g.nome}")
            for g in cd_queryset
        ]

    else:
        cd_choices = []
        if user_cd:
            cd_choices = [
                (user_cd.id, f"{user_cd.cod_iata} - {user_cd.nome}")
            ]
        else:
            cd_choices = [("", "Sem designação configurada")]

    form = GerenciamentoEstoqueForm(
        nome_form=titulo,
        client_choices=client_choices,
        cd_choices=cd_choices
    )

    if request.method == 'POST':
        pass

    return render(request, "logistica/gerenciamento_estoque.html", {
        "form": form,
        "titulo": titulo,
        "botao_texto": "Consultar",
        "site_title": titulo,
    })
