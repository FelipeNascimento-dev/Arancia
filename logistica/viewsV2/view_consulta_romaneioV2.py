import re
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import RomaneioConsultaForm
from django.db.models.functions import Lower
from ..models import GroupAditionalInformation, Group
from setup.local_settings import STOCK_API_URL
from django.contrib.auth.decorators import login_required, permission_required

JSON_CT = "application/json"


def _extract_next(result):
    if not isinstance(result, dict):
        return None
    for k in ("proximo", "next", "next_romaneio", "next_rom", "available"):
        if k in result and result[k]:
            return str(result[k]).strip().upper()
    return None


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def consult_romV2(request):
    titulo = "Consultar Romaneio"
    proximo_disponivel = None
    botao_texto = "Consultar"
    result = None
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

    try:
        pa_tatuape = GroupAditionalInformation.objects.get(
            nome__iexact="Tatuapé"
        )

        destination_choices.append({
            "id": pa_tatuape.id,
            "label": "PA Tatuapé"
        })

    except GroupAditionalInformation.DoesNotExist:
        pass

    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST, nome_form=titulo)
        if "criar_romaneio" in request.POST:
            modal_origin = True

        if "confirmar_origem" in request.POST:
            if can_choose_origin:
                origin_id = request.POST.get("origin_id")
            else:
                origin_id = location_id

            destination_id = pa_tatuape.id

            if not origin_id or not destination_id:
                messages.error(request, "Selecione origem e destino")
                modal_origin = True
            else:
                url_post = f"{STOCK_API_URL}/v2/romaneios/"
                payload = {
                    "created_by": request.user.username,
                    "location_id": location_id,
                    "client_name": "cielo",
                    "origin_id": int(origin_id),
                    "destination_id": int(destination_id),
                }

                client_post = RequestClient(
                    url=url_post,
                    method="POST",
                    headers={"Accept": JSON_CT,
                             "Content-Type": "application/json"},
                    request_data=payload,
                )
                result = client_post.send_api_request()

                if isinstance(result, dict) and result.get("romaneio"):
                    rom = result.get("romaneio")

                    request.session["romaneio_num"] = rom
                    request.session["result"] = result

                    request.session["reverse_origin_id"] = int(origin_id)
                    request.session["reverse_destination_id"] = int(
                        destination_id)

                    request.session["reverse_origin_label"] = result.get(
                        "origin")
                    request.session["reverse_destination_label"] = result.get(
                        "destination")

                    request.session.modified = True

                    messages.success(
                        request, f"Romaneio {rom} criado com sucesso!")
                    return redirect("logistica:reverse_createV2")

                messages.error(request, f"Erro ao criar romaneio: {result}")
                return render(request, "logistica/templatesV2/consulta_romaneioV2.html", {
                    "form": form,
                    "botao_texto": botao_texto,
                    "site_title": titulo,
                    "proximo_disponivel": proximo_disponivel,
                })

        if "enviar_evento" in request.POST:
            if form.is_valid():
                numero = form.cleaned_data["numero"]
                url_get = f"{STOCK_API_URL}/v1/romaneios/{numero}?location_id={location_id}"
                client_get = RequestClient(
                    url=url_get,
                    method="GET",
                    headers={"Accept": JSON_CT},
                )
                result = client_get.send_api_request()

                if isinstance(result, dict) and result.get("romaneio"):
                    request.session["romaneio_num"] = result.get("romaneio")
                    request.session["result"] = result
                    request.session["reverse_origin_id"] = result.get(
                        "origin_id")
                    request.session["reverse_destination_id"] = result.get(
                        "destination_id")
                    request.session["reverse_origin_label"] = result.get(
                        "origin")
                    request.session["reverse_destination_label"] = result.get(
                        "destination")
                    request.session.modified = True

                    messages.success(
                        request, f"Romaneio {result.get('romaneio')} encontrado!")
                    return redirect("logistica:reverse_createV2")

                proximo_disponivel = _extract_next(result)
                if not proximo_disponivel:
                    proximo_disponivel = numero or "AR00001"

                messages.warning(
                    request,
                    f"O romaneio {numero} não existe."
                )
                botao_texto = "Consultar novamente"

                return render(request, "logistica/templatesV2/consulta_romaneioV2.html", {
                    "form": form,
                    "botao_texto": botao_texto,
                    "site_title": titulo,
                    "proximo_disponivel": proximo_disponivel,
                    "result": result
                })

    form = RomaneioConsultaForm(nome_form=titulo)
    return render(request, "logistica/templatesV2/consulta_romaneioV2.html", {
        "form": form,
        "botao_texto": botao_texto,
        "modal_origin": modal_origin,
        'origin_choices': origin_choices,
        'destination_choices': destination_choices,
        'can_choose_origin': can_choose_origin,
        'origin_label': origin_label,
        "site_title": titulo,
        "proximo_disponivel": proximo_disponivel,
        "result": result,
        "current_parent_menu": "logistica",
        "current_menu": "lastmile",
        "current_submenu": "reverse",
        "current_subsubmenu": "consultar_romaneio"
    })
