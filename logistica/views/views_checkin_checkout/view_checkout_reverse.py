from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from ...forms import CheckOutForm
from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient
from django.contrib import messages
from django.db.models.functions import Lower
from ...models import GroupAditionalInformation, Group

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def checkout_reverse(request, vetor):
    titulo = 'Consultar Romaneio'
    form = CheckOutForm(request.POST, nome_form=titulo)

    modal_origin = False

    user = request.user
    can_choose_origin = request.user.has_perm("logistica.gestao_total")
    sales_channel = user.designacao.informacao_adicional.sales_channel
    if sales_channel == 'all':
        location_id = 0
    else:
        location_id = user.designacao.informacao_adicional_id

    origin_label = None

    if not can_choose_origin and location_id:
        try:
            origin_obj = GroupAditionalInformation.objects.get(id=location_id)
            origin_label = origin_obj.nome
        except GroupAditionalInformation.DoesNotExist:
            origin_label = None

    cliente_selecionado = request.session.get("selected_client")

    client_code = None
    client_name = None

    if cliente_selecionado:
        client_code = cliente_selecionado.get("client_code")
        client_name = cliente_selecionado.get("client_name")

    origin_choices = []

    if can_choose_origin:
        try:
            grupo_pa = Group.objects.get(name="arancia_PA")

            origin_qs = (
                GroupAditionalInformation.objects
                .filter(group=grupo_pa)
                .annotate(nome_lower=Lower("nome"))
                .order_by("nome_lower")
                .values("id", "nome")
            )

            for o in origin_qs:
                origin_choices.append({
                    "id": o["id"],
                    "label": o["nome"]
                })
        except Group.DoesNotExist:
            pass

    destination_choices = []

    grupos = Group.objects.filter(name__in=["arancia_PA", "arancia_CD"])

    destinos = (
        GroupAditionalInformation.objects
        .filter(group__in=grupos)
        .select_related("group")
        .annotate(nome_lower=Lower("nome"))
        .order_by("group__name", "nome_lower")
    )

    for d in destinos:
        if d.group.name == "arancia_PA":
            label = f"[PA] {d.nome}"
        elif d.group.name == "arancia_CD":
            label = f"[CD] {d.nome}"
        else:
            label = d.nome

        destination_choices.append({
            "id": d.id,
            "label": label
        })

    if request.method == 'POST':
        if 'novo_romaneio' in request.POST:
            modal_origin = True

        elif 'confirmar_origem' in request.POST:
            if can_choose_origin:
                origin_id = request.POST.get("origin_id")
            else:
                origin_id = location_id
            destination_id = request.POST.get("destination_id")

            if not origin_id or not destination_id:
                messages.error(request, "Selecione origem e destino")
                modal_origin = True
            else:
                url_post = f"{STOCK_API_URL}/v2/romaneios/"

                payload = {
                    "created_by": request.user.username,
                    "location_id": location_id,
                    "client_name": client_code,
                    "origin_id": int(origin_id),
                    "destination_id": int(destination_id),
                }

                client_post = RequestClient(
                    url=url_post,
                    method="POST",
                    headers={
                        "Accept": JSON_CT,
                        "Content-Type": JSON_CT,
                    },
                    request_data=payload,
                )

                print(payload)

                result = client_post.send_api_request()

                numero_rom = result.get('romaneio')

                if isinstance(result, dict):
                    messages.success(request, "Romaneio criado com sucesso")
                    return redirect("logistica:checkout_reverse_create", rom=numero_rom)

                messages.error(request, "Erro ao criar romaneio")
                modal_origin = True

        if 'enviar_evento' in request.POST:
            numero_romaneio = request.POST.get("numero_romaneio")

            url_get = f"{STOCK_API_URL}/v1/romaneios/{numero_romaneio}?location_id={location_id}"
            client_get = RequestClient(
                url=url_get,
                method="GET",
                headers={"Accept": JSON_CT},
            )
            result = client_get.send_api_request()

            if isinstance(result, dict) and result.get("romaneio"):
                numero_rom = result.get('romaneio')

                request.session["romaneio_num"] = result.get("romaneio")
                request.session["result"] = result
                messages.success(
                    request, f"Romaneio {result.get('romaneio')} encontrado!")
                return redirect("logistica:checkout_reverse_create", rom=numero_rom)
    return render(
        request,
        'logistica/templates_checkin_checkout/checkout_reverse.html', {
            'form': form,
            'botao_texto': 'Consultar',
            'modal_origin': modal_origin,
            'client_code': client_code,
            'client_name': client_name,
            'origin_choices': origin_choices,
            'destination_choices': destination_choices,
            'can_choose_origin': can_choose_origin,
            'origin_label': origin_label,
        })
