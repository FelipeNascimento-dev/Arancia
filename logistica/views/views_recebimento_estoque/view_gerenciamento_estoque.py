from ...forms import GerenciamentoEstoqueForm
from django.shortcuts import render
from django.contrib import messages
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from django.contrib.auth.decorators import login_required, permission_required
import json
from ...models import GroupAditionalInformation
from urllib.parse import quote

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.gerente_estoque', raise_exception=True)
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

    form = GerenciamentoEstoqueForm(
        nome_form=titulo,
        client_choices=client_choices,
        cd_choices=cd_choices,
        data=request.POST or None
    )

    resultado_itens = None

    if request.method == "POST" and "enviar_evento" in request.POST:

        if form.is_valid():
            client = form.cleaned_data["client"]
            cd_id = int(form.cleaned_data["cd_estoque"])
            sales_channel = sales_channels_map.get(cd_id, "")
            status = request.POST.get("status", "IN_DEPOT")
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

                if isinstance(result, dict) and "items" in result:
                    resultado_itens = result["items"]
                elif isinstance(result, list):
                    resultado_itens = result
                else:
                    resultado_itens = []

            except Exception as e:
                messages.error(request, f"Erro ao buscar itens: {e}")
                resultado_itens = []

    return render(
        request,
        "logistica/templates_gerenciamento_estoque/gerenciamento_estoque.html",
        {
            "form": form,
            "resultado_itens": resultado_itens,
            "titulo": titulo,
            "botao_texto": "Consultar",
            "site_title": titulo,
        }
    )
