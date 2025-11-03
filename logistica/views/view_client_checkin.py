from ..forms import ClientCheckInForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import Group
from ..models import GroupAditionalInformation


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def client_checkin(request):
    client_data = request.session.get("selected_client", {})
    client_name = client_data.get("client_name", "Cliente não selecionado")
    titulo = f"Check-In {client_name}"

    pedido_atrelado = request.session.get("order", "")

    try:
        grupos = GroupAditionalInformation.objects.filter(
            group__name__iregex=r'arancia_(PA|CD)'
        ).select_related("group").order_by("group__name")

        from_choices = [
            (
                str(g.group.id),
                f"{g.group.name} - {g.nome or g.razao_social or 'Sem nome'}"
            )
            for g in grupos
        ]

        if not from_choices:
            from_choices = [("", "Nenhum PA/CD encontrado")]

    except Exception as e:
        messages.error(request, f"Erro ao carregar grupos: {e}")
        from_choices = [("", "Erro ao carregar origens")]

    if request.method == "POST":
        form = ClientCheckInForm(
            request.POST,
            nome_form=titulo,
            from_choices=from_choices
        )
    else:
        initial_data = {"pedido_atrelado": pedido_atrelado}
        form = ClientCheckInForm(
            nome_form=titulo,
            initial=initial_data,
            from_choices=from_choices
        )

    return render(
        request,
        "logistica/client_checkin.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Registrar Check-In",
        },
    )
