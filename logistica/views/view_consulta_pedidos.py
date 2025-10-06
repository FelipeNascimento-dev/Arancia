from urllib.parse import quote as urlquote
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.urls import reverse

from setup.local_settings import API_URL
from utils.request import RequestClient
from ..forms import ConsultaPedForm
from ..models import GroupAditionalInformation

PERM_GERENCIAR = "logistica.pode_gerenciar_filiais"
JSON_CT = "application/json"


def get_user_sales_channel(user):
    if not user.has_perm(PERM_GERENCIAR):
        sc = None
        if getattr(user, 'designacao', None) and user.designacao.informacao_adicional:
            gai = user.designacao.informacao_adicional
            if getattr(gai, 'group', None) and gai.group.name == "arancia_PA":
                sc = (gai.sales_channel or "").strip()
        return [sc] if sc else []

    qs = (
        GroupAditionalInformation.objects
        .filter(group__name="arancia_PA")
        .exclude(sales_channel__isnull=True)
        .exclude(sales_channel__exact="")
        .values_list("sales_channel", flat=True)
        .distinct()
    )

    sales_channels = sorted(
        {(sc or "").strip() for sc in qs if sc},
        key=lambda s: s.lower()
    )
    return sales_channels


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def consulta_pedidos(request):
    sales_channels = [sc for sc in get_user_sales_channel(request.user) if sc]
    choices = [(sc, sc) for sc in sales_channels]

    tabela_dados = None

    if request.method == "POST":
        form = ConsultaPedForm(request.POST, sales_channel_choices=choices)

        if form.is_valid():
            sc = form.cleaned_data["sales_channel"]

            url = f"{API_URL}/api/order-sumary/{sc}/json"
            client = RequestClient(
                url=url,
                method="GET",
                headers={"Accept": JSON_CT},
            )
            try:
                result = client.send_api_request()
                if isinstance(result, (list, dict)):
                    tabela_dados = result
                else:
                    result.raise_for_status()
                    tabela_dados = result.json()

                if not tabela_dados:
                    messages.info(
                        request, "Nenhum registro encontrado para o canal selecionado.")
                else:
                    messages.success(
                        request, f"Consulta realizada para o canal: {sc}")

            except Exception as e:
                tabela_dados = None
                messages.error(request, f"Erro ao consultar a API: {e}")
    else:
        form = ConsultaPedForm(sales_channel_choices=choices)

    if not sales_channels:
        messages.info(
            request, "Nenhum sales_channel disponível para seus grupos.")

    return render(request, "logistica/consulta_pedidos.html", {
        "form": form,
        "form_action": reverse("logistica:consulta_pedidos"),
        "botao_texto": "Consultar",
        "site_title": "Consulta de Pedidos",
        "tabela_dados": tabela_dados,
    })
