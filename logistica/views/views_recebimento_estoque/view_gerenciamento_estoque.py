from datetime import datetime
from collections import Counter
from ...forms import GerenciamentoEstoqueForm
from django.shortcuts import render
from django.contrib import messages
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from django.contrib.auth.decorators import login_required, permission_required
from ...models import GroupAditionalInformation
from urllib.parse import quote
import json

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.gerente_estoque', raise_exception=True)
def gerenciamento_estoque(request):
    titulo = "Gerenciamento de Estoque"
    user = request.user

    # ==============================
    # Buscar Clientes
    # ==============================
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

    # ==============================
    # Buscar CDs acessíveis ao usuário
    # ==============================
    user_cd = getattr(user.designacao, "informacao_adicional", None)
    sales_channels_map = {}
    cd_choices = []

    if user.has_perm("logistica.gerente_estoque"):
        cd_queryset = GroupAditionalInformation.objects.filter(
            group__name__icontains="arancia_pa"
        )
        for g in cd_queryset:
            cd_choices.append((g.id, f"{g.cod_iata} - {g.nome}"))
            sales_channels_map[g.id] = g.sales_channel
    else:
        if user_cd:
            cd_choices = [(user_cd.id, f"{user_cd.cod_iata} - {user_cd.nome}")]
            sales_channels_map[user_cd.id] = user_cd.sales_channel
        else:
            cd_choices = [("", "Sem designação configurada")]

    # ==============================
    # Formulário
    # ==============================
    form = GerenciamentoEstoqueForm(
        nome_form=titulo,
        client_choices=client_choices,
        cd_choices=cd_choices,
        data=request.POST or None
    )

    resultado_itens = []
    totais = {"total_geral": 0, "por_status": {}, "por_produto": {}}
    produtos_unicos = []

    # ==============================
    # SUBMISSÃO DO FORM
    # ==============================
    if request.method == "POST" and "enviar_evento" in request.POST:
        if form.is_valid():

            client = form.cleaned_data["client"]
            cd_id = int(form.cleaned_data["cd_estoque"])
            status = request.POST.get("status", "IN_DEPOT")

            sales_channel = sales_channels_map.get(cd_id, "")
            sales_channel_encoded = quote(str(sales_channel), safe='')

            url = (
                f"{STOCK_API_URL}/v1/items/list/{client}"
                f"?status={status}"
                f"&sales_channels%5B%5D={sales_channel_encoded}"
            )

            try:
                req = RequestClient(url=url, method="GET",
                                    headers={"Accept": JSON_CT})
                result = req.send_api_request()

                if isinstance(result, str):
                    result = json.loads(result)

                # ==============================
                # Garante que retorno seja sempre lista de dicts
                # ==============================
                if isinstance(result, dict) and "items" in result:
                    resultado_itens = result["items"]
                elif isinstance(result, list):
                    resultado_itens = result
                else:
                    resultado_itens = []

                # Remove qualquer item inválido (int, None, string, bool, etc.)
                resultado_itens = [
                    i for i in resultado_itens if isinstance(i, dict)]

                # ==============================
                # CONTAGENS
                # ==============================
                totais["total_geral"] = len(resultado_itens)

                totais["por_status"] = dict(Counter(
                    i.get("status", "DESCONHECIDO") for i in resultado_itens
                ))

                totais["por_produto"] = dict(Counter(
                    i.get("product_id", "SEM PRODUTO") for i in resultado_itens
                ))

                produtos_unicos = sorted(list(set(
                    i.get("product_id")
                    for i in resultado_itens
                    if i.get("product_id")
                )))

                # ==============================
                # FILTRO POR PRODUTO
                # ==============================
                filtro_produto = request.POST.get("produto")
                if filtro_produto:
                    resultado_itens = [
                        i for i in resultado_itens
                        if str(i.get("product_id")) == filtro_produto
                    ]

            except Exception as e:
                messages.error(request, f"Erro ao buscar itens: {e}")
                resultado_itens = []

    # ==============================
    # RENDERIZAÇÃO
    # ==============================
    return render(
        request,
        "logistica/templates_recebimento_estoque/gerenciamento_estoque.html",
        {
            "form": form,
            "resultado_itens": resultado_itens,
            "totais": totais,
            "produtos_unicos": produtos_unicos,
            "titulo": titulo,
            "botao_texto": "Consultar",
            "site_title": titulo,
        }
    )
