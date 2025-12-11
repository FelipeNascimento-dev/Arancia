from datetime import datetime
from collections import Counter
from urllib.parse import quote
import json

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

from ...forms import GerenciamentoEstoqueForm
from ...models import GroupAditionalInformation

# IMPORTA AS DUAS FUNÇÕES (ARQUIVOS SEPARADOS)
from .func_visao_resumida import func_visao_resumida
from .func_visao_detalhada import func_visao_detalhada


JSON_CT = "application/json"


def carregar_formulario(request):
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

    user = request.user
    user_cd = getattr(user.designacao, "informacao_adicional", None)

    sales_channels_map = {}
    cd_choices = []

    if user.has_perm("logistica.gerente_estoque"):
        queryset = GroupAditionalInformation.objects.filter(
            group__name__icontains="arancia_pa"
        )
        for g in queryset:
            cd_choices.append((g.id, f"{g.cod_iata} - {g.nome}"))
            sales_channels_map[g.id] = g.sales_channel
    else:
        if user_cd:
            cd_choices.append(
                (user_cd.id, f"{user_cd.cod_iata} - {user_cd.nome}"))
            sales_channels_map[user_cd.id] = user_cd.sales_channel
        else:
            cd_choices.append(("", "Sem designação configurada"))

    form = GerenciamentoEstoqueForm(
        nome_form="Gerenciamento de Estoque",
        client_choices=client_choices,
        cd_choices=cd_choices,
        data=request.POST or None
    )

    return form, client_choices, cd_choices, sales_channels_map


@login_required(login_url='logistica:login')
@permission_required('logistica.gerente_estoque', raise_exception=True)
def gerenciamento_estoque(request):
    titulo = "Gerenciamento de Estoque"

    form, client_choices, cd_choices, sales_channels_map = carregar_formulario(
        request)

    resultado_itens = []
    totais = {}
    produtos_unicos = []
    visao = "detalhe"

    if request.method == "POST":
        visao = request.POST.get("visao", "detalhe")

        if form.is_valid():

            if visao == "resumo":
                resultado_itens, totais, produtos_unicos = func_visao_resumida(
                    request, form, sales_channels_map
                )

            elif visao == "detalhe":
                resultado_itens, totais, produtos_unicos = func_visao_detalhada(
                    request, form, sales_channels_map
                )

    pa_selecionadas = request.POST.getlist(
        "cd_estoque") if request.method == "POST" else []

    return render(
        request,
        "logistica/templates_recebimento_estoque/gerenciamento_estoque.html",
        {
            "form": form,
            "resultado_itens": resultado_itens,
            "pa_selecionadas": pa_selecionadas,
            "totais": totais,
            "produtos_unicos": produtos_unicos,
            "visao": visao,
            "titulo": titulo,
            "botao_texto": 'Consultar',
            "site_title": titulo
        }
    )
