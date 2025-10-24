import re
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import RomaneioConsultaForm
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
def consult_rom(request):
    titulo = "Consultar Romaneio"
    proximo_disponivel = None
    botao_texto = "Consultar"
    result = None

    user = request.user
    sales_channel = user.designacao.informacao_adicional.sales_channel
    if sales_channel == 'all':
        location_id = 0
    else:
        location_id = user.designacao.informacao_adicional_id

    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST, nome_form=titulo)
        if form.is_valid():

            if "criar_romaneio" in request.POST:
                # numero_criar = request.POST.get(
                #     "criar_romaneio", "").strip().upper()
                # normalizado = (numero_criar)
                # if not normalizado:
                #     messages.error(
                #         request, "Formato inválido. Use AR00001 (AR + 5 dígitos).")
                #     return render(request, "logistica/consult_rom.html", {
                #         "form": form,
                #         "botao_texto": botao_texto,
                #         "site_title": titulo,
                #         "proximo_disponivel": proximo_disponivel,
                #     })

                url_post = f"{STOCK_API_URL}/v1/romaneios/"
                payload = {
                    "created_by": user.username,
                    "location_id": user.designacao.informacao_adicional_id,
                    "client_name": "cielo"
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
                    messages.success(
                        request, f"Romaneio {rom} criado com sucesso!")
                    return redirect("logistica:reverse_create")

                messages.error(
                    request, f"Erro ao criar romaneio: {result}")
                return render(request, "logistica/consult_rom.html", {
                    "form": form,
                    "botao_texto": botao_texto,
                    "site_title": titulo,
                    "proximo_disponivel": proximo_disponivel,
                })

            else:
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
                    messages.success(
                        request, f"Romaneio {result.get('romaneio')} encontrado!")
                    return redirect("logistica:reverse_create")

                proximo_disponivel = _extract_next(result)
                if not proximo_disponivel:
                    proximo_disponivel = numero or "AR00001"

                messages.warning(
                    request,
                    f"O romaneio {numero} não existe."
                )
                botao_texto = "Consultar novamente"

                return render(request, "logistica/consult_rom.html", {
                    "form": form,
                    "botao_texto": botao_texto,
                    "site_title": titulo,
                    "proximo_disponivel": proximo_disponivel,
                    "result": result
                })

    form = RomaneioConsultaForm(nome_form=titulo)
    return render(request, "logistica/consult_rom.html", {
        "form": form,
        "botao_texto": botao_texto,
        "site_title": titulo,
        "proximo_disponivel": proximo_disponivel,
        "result": result
    })
