from urllib.parse import quote as urlquote
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from ..forms import ConsultaPedForm
from ..models import GroupAditionalInformation


@login_required
def consulta_pedidos(request):

    qs = (
        GroupAditionalInformation.objects
        .exclude(sales_channel__isnull=True)
        .exclude(sales_channel__exact="")
    )

    if not request.user.is_superuser:
        user_groups = request.user.groups.all()
        qs = qs.filter(group__in=user_groups)

    sales_channels = list(
        qs.values_list("sales_channel", flat=True).distinct().order_by(
            "sales_channel")
    )

    choices = [("", "Selecione...")] + [(sc, sc) for sc in sales_channels]

    if request.method == "POST":
        form = ConsultaPedForm(request.POST)
        form.fields["sales_channel"].choices = choices

        if form.is_valid():
            sc = form.cleaned_data["sales_channel"]
            messages.success(request, f"Canal selecionado: {sc}")
            url = reverse("logistica:consulta_pedidos")
            return redirect(f"{url}?sales_channel={urlquote(sc)}")
    else:
        form = ConsultaPedForm()
        form.fields["sales_channel"].choices = choices

    if not sales_channels:
        messages.info(
            request, "Nenhum sales_channel disponível para seus grupos.")

    return render(request, "logistica/consulta_pedidos.html", {
        "form": form,
        'botao_texto': 'Consultar',
        'site_title': 'Consulta de Pedidos',
    })
