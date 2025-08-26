from urllib.parse import quote as urlquote
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.urls import reverse
from ..forms import ConsultaPedForm
from ..models import GroupAditionalInformation

PERM_GERENCIAR = "logistica.pode_gerenciar_filiais"


def get_user_sales_channel(user):

    if not user.has_perm(PERM_GERENCIAR):
        sales_channel = (
            user.designacao.informacao_adicional.sales_channel
            if user.designacao and user.designacao.informacao_adicional
            else None
        )

        return [sales_channel]

    qs_base = (
        GroupAditionalInformation.objects
        .exclude(sales_channel__isnull=True)
        .exclude(sales_channel__exact="")
        .distinct()
    )
    sales_channels = []
    for item in qs_base:
        if item.sales_channel not in sales_channels:
            sales_channels.append(item.sales_channel)
    return sales_channels


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def consulta_pedidos(request):
    sales_channels = get_user_sales_channel(request.user)
    choices = [(sc, sc) for sc in sales_channels]

    if request.method == "POST":
        form = ConsultaPedForm(request.POST, sales_channel_choices=choices)
        if form.is_valid():
            sc = form.cleaned_data["sales_channel"]
            messages.success(request, f"Canal selecionado: {sc}")
            url = reverse("logistica:consulta_pedidos")
            return redirect(f"{url}?sales_channel={urlquote(sc)}")
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
    })
