from datetime import datetime
from collections import Counter
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from ...forms import GerenciamentoEstoqueForm
from ...models import GroupAditionalInformation
from .func_visao_resumida import func_visao_resumida
from .func_visao_detalhada import func_visao_detalhada
from urllib.parse import urlencode


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

    cd_choices = []
    sales_channels_map = {}

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
@permission_required('logistica.acesso_arancia', raise_exception=True)
def gerenciamento_estoque(request):
    titulo = "Gerenciamento de Estoque"

    if request.method == "POST" and "exportar" in request.POST:

        form, _, _, sales_channels_map = carregar_formulario(request)

        if not form.is_valid():
            messages.error(request, "Filtros inválidos para exportação.")
            return redirect(request.path)

        client = form.cleaned_data["client"]
        cds = form.cleaned_data["cd_estoque"]
        status = request.POST.get("status", "IN_DEPOT")

        if not client:
            messages.error(request, "Selecione um cliente.")
            return redirect(request.path)

        if not cds:
            messages.error(request, "Selecione ao menos um CD.")
            return redirect(request.path)

        pa_ids = [int(i) for i in form.cleaned_data["cd_estoque"]]

        stock_type = request.POST.get("stock_type")

        if stock_type:
            stock_type = stock_type.strip()

        query_params = [
            ("status", status),
            ("offset", 0),
            ("limit", 1000),
        ]

        if stock_type:
            query_params.append(("stock_type", stock_type))

        for pa in pa_ids:
            query_params.append(("locations_ids", pa))

        qs = urlencode(query_params, doseq=True)

        export_url = (
            f"{STOCK_API_URL}/v1/items/list-byid/export/{client}?{qs}"
        )

        return redirect(export_url)

    if request.method == "POST" and "item_id" in request.POST:

        item_id = request.POST["item_id"]
        novo_produto = request.POST["novo_produto"]

        payload = {"product_id": int(novo_produto)}
        url = f"{STOCK_API_URL}/v1/items/{item_id}"

        api = RequestClient(
            url=url,
            method="PUT",
            headers={"Content-Type": "application/json",
                     "Accept": "application/json"},
            request_data=payload
        )

        resp = api.send_api_request()

        if isinstance(resp, dict) and resp.get("detail") is None:
            messages.success(request, "Produto atualizado com sucesso!")
        else:
            messages.error(request, f"Erro ao atualizar produto: {resp}")

        filtros = request.session.get("estoque_filtros")

        if filtros:
            new_post = request.POST.copy()
            new_post["client"] = filtros["client"]
            new_post["visao"] = filtros["visao"]
            new_post["limit"] = filtros["limit"]
            new_post["offset"] = filtros["offset"]
            new_post["status"] = filtros["status"]
            new_post.setlist("cd_estoque", filtros["cd_estoque"])
            request.POST = new_post
        else:
            return redirect(request.path)

    form, client_choices, cd_choices, sales_channels_map = carregar_formulario(
        request)

    produtos_api = []
    resultado_itens = []
    totais = {}
    produtos_unicos = []
    visao = request.POST.get("visao", "detalhe")
    limit = int(request.POST.get("limit", 25))
    offset = int(request.POST.get("offset", 0))
    has_more = False
    page_number = 1
    total_pages = 1

    if request.method == "POST" and form.is_valid():

        if visao == "resumo":
            resultado_itens, totais, produtos_unicos = func_visao_resumida(
                request, form, sales_channels_map
            )
        else:
            (
                resultado_itens,
                totais,
                produtos_unicos,
                limit,
                offset,
                has_more,
                total_pages,
                page_number,
                produtos_api,
            ) = func_visao_detalhada(request, form, sales_channels_map)

        request.session["estoque_filtros"] = {
            "client": form.cleaned_data["client"],
            "cd_estoque": form.cleaned_data["cd_estoque"],
            "limit": limit,
            "offset": offset,
            "visao": visao,
            "status": request.POST.get("status", "IN_DEPOT"),
        }

    pa_selecionadas = request.POST.getlist(
        "cd_estoque") if request.method == "POST" else []

    stock_types = []

    client_post = request.POST.get("client")
    if client_post:
        try:
            url = f"{STOCK_API_URL}/v1/origins/{client_post}"
            resp = RequestClient(
                url=url,
                method="GET",
                headers={"Accept": JSON_CT}
            ).send_api_request()

            if isinstance(resp, str):
                resp = json.loads(resp)

            stock_types = [
                i.get("stock_type")
                for i in resp
                if i.get("stock_type")
            ]

        except Exception:
            stock_types = []

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
            "site_title": titulo,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
            "total_pages": total_pages,
            "page_number": page_number,
            "next_offset": offset + limit,
            "prev_offset": max(offset - limit, 0),
            "produtos_api": produtos_api,
            "stock_types": stock_types,
        }
    )
