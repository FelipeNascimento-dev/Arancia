from django.contrib import messages
from django.shortcuts import render, redirect
from setup.local_settings import API_URL
from utils.request import RequestClient
from ...models import GroupAditionalInformation, UserDesignation
from ...forms import RecebimentoRemessaForm
from django.contrib.auth.decorators import login_required, permission_required

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def recebimento_remessa(request):
    titulo = 'Recebimento por Remessa'

    serials = request.session.get("rr_serials", [])
    order_number = request.session.get("rr_order_number", "")
    from_location_sess = request.session.get("rr_from_location", "")
    to_location_sess = request.session.get("rr_to_location", "")

    origem_queryset = GroupAditionalInformation.objects.filter(
        group__name__in=["arancia_CD", "arancia_PA"]
    )

    origem_choices = [
        (g.id, f"{g.cod_iata} - {g.nome}") for g in origem_queryset
    ]

    user = request.user
    destino_obj = getattr(user.designacao, "informacao_adicional", None)

    if destino_obj:
        if user.designacao.informacao_adicional.sales_channel == 'all':
            destino_queryset = GroupAditionalInformation.objects.filter(
                group__name__in=["arancia_PA"]
            )
            destino_choices = [
                (g.id, f"{g.cod_iata} - {g.nome}") for g in destino_queryset
            ]
        else:
            destino_choices = [
                (destino_obj.id, f"{destino_obj.cod_iata} - {destino_obj.nome}")]
    else:
        destino_choices = [("", "Sem designação configurada")]

    if request.method == "POST":
        if "order_number" in request.POST:
            pedido_digitado = request.POST.get("order_number", "").strip()
            request.session["rr_order_number"] = pedido_digitado
            order_number = pedido_digitado
        if "from_location" in request.POST:
            from_location_sess = request.POST.get("from_location")
            request.session["rr_from_location"] = from_location_sess

    if request.method == "POST" and "add_serial" in request.POST:
        novo = request.POST.get("box_codes", "").strip().upper()
        if novo:
            if novo not in serials:
                serials.append(novo)
                request.session["rr_serials"] = serials
            else:
                messages.warning(request, "Serial já inserido.")
        return redirect("logistica:recebimento_remessa")

    if request.method == "POST" and "remove_serial" in request.POST:
        idx = int(request.POST.get("remove_serial"))
        if 0 <= idx < len(serials):
            serials.pop(idx)
            request.session["rr_serials"] = serials
        return redirect("logistica:recebimento_remessa")

    if request.method == "POST" and "clear_serials" in request.POST:
        request.session["rr_serials"] = []
        return redirect("logistica:recebimento_remessa")

    if request.method == "POST" and "box_codes" in request.POST and "enviar_evento" not in request.POST:
        novo = request.POST.get("box_codes", "").strip().upper()
        if novo:
            if novo not in serials:
                serials.append(novo)
                request.session["rr_serials"] = serials
            else:
                messages.warning(request, "Serial já inserido.")
        return redirect("logistica:recebimento_remessa")

    if request.method == "POST" and "enviar_evento" in request.POST:
        form = RecebimentoRemessaForm(request.POST, nome_form=titulo)
        form.fields['from_location'].choices = origem_choices
        form.fields['to_location'].choices = destino_choices

        if not serials:
            messages.error(
                request, "Insira pelo menos 1 serial antes de enviar.")
        elif form.is_valid():
            from_location_id = int(
                form.cleaned_data.get("from_location") or 0)
            to_location_id = user.designacao.informacao_adicional.id

            url = f"{API_URL}/api/v2/trackings/send"
            payload = {
                "order_number": order_number,
                "volume_number": 1,
                "order_type": "NORMAL",
                "tracking_code": "208",
                "bar_codes": serials,
                "to_location_id": to_location_id,
                "from_location_id": from_location_id,
                "created_by": user.username
            }

            res = RequestClient(
                url=url,
                method="POST",
                headers={"Accept": JSON_CT},
                request_data=payload
            )
            result = res.send_api_request()
            if isinstance(result, dict) and result.get('detail'):
                messages.error(request, f"{result['detail']}")
            else:
                messages.success(request, "Tracking enviada com sucesso!")
                request.session["rr_serials"] = []
                request.session.pop("rr_order_number", None)
                request.session.pop("rr_from_location", None)
                request.session.pop("rr_to_location", None)
                request.session.pop("rr_serials", None)
                return redirect("logistica:client_select")

    else:
        form = RecebimentoRemessaForm(nome_form=titulo)
        form.fields["from_location"].choices = origem_choices
        form.fields["to_location"].choices = destino_choices
        form.fields["order_number"].initial = order_number
        form.fields["from_location"].initial = from_location_sess
        form.fields["to_location"].initial = to_location_sess

    return render(
        request,
        "logistica/templates_recebimento_estoque/recebimento_remessa.html",
        {
            "form": form,
            "serials": serials,
            "botao_texto": "Consultar",
            "site_title": titulo,
            "etapa_ativa": "recebimento_remessa",
        },
    )
