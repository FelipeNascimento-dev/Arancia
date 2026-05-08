from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient


# @login_required(login_url='logistica:login')
# @permission_required('logistica.acesso_arancia', raise_exception=True)
# @permission_required('transportes.ver_transportes', raise_exception=True)
# def buscar_motoristas_travels(request):
#     nome = (request.GET.get("nome") or "").strip()
#     carrier_id = (request.GET.get("carrier_id") or "").strip()

#     if not carrier_id:
#         return JsonResponse({
#             "items": [],
#             "detail": "Transportadora não informada."
#         }, status=400)

#     if len(nome) < 2:
#         return JsonResponse({
#             "items": []
#         })

#     params = {
#         "Nome": nome,
#         "carrier_id": carrier_id,
#         "limit": 20,
#         "offset": 0,
#     }

#     url = f"{TRANSP_API_URL}/Carriers/driver/list?{urlencode(params)}"

#     client = RequestClient(
#         method="GET",
#         url=url,
#         headers={
#             "accept": "application/json",
#             "Content-Type": "application/json",
#         },
#     )

#     response_api = client.send_api_request()

#     print("URL MOTORISTAS:", url)
#     print("RESPOSTA MOTORISTAS:", response_api)

#     if isinstance(response_api, dict) and response_api.get("detail"):
#         return JsonResponse({
#             "items": [],
#             "detail": response_api.get("detail")
#         }, status=400)

#     if isinstance(response_api, list):
#         drivers = response_api
#     elif isinstance(response_api, dict):
#         drivers = (
#             response_api.get("items")
#             or response_api.get("results")
#             or response_api.get("data")
#             or []
#         )
#     else:
#         drivers = []

#     items = []

#     for driver in drivers:
#         if not isinstance(driver, dict):
#             continue

#         driver_id = (
#             driver.get("uid")
#             or driver.get("driver_id")
#             or driver.get("id")
#         )

#         driver_name = (
#             driver.get("name")
#             or driver.get("nome")
#             or driver.get("Nome")
#             or driver.get("driver_name")
#         )

#         if not driver_id or not driver_name:
#             continue

#         items.append({
#             "uid": driver_id,
#             "name": driver_name,
#             "id": driver.get("id"),
#             "carrier_id": carrier_id,
#         })

#     return JsonResponse({
#         "items": items
#     })


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.ver_transportes', raise_exception=True)
def atribuir_motorista_viagens_manual(request):
    titulo = "Atribuir Motorista às Viagens"

    url_transportadora = f"{TRANSP_API_URL}/Carriers/list"

    client = RequestClient(
        method="GET",
        url=url_transportadora,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    )

    resp_transportadora_api = client.send_api_request()

    if isinstance(resp_transportadora_api, dict) and resp_transportadora_api.get("detail"):
        carriers = []
        messages.error(request, resp_transportadora_api.get("detail"))

    elif isinstance(resp_transportadora_api, dict):
        carriers = (
            resp_transportadora_api.get("items")
            or resp_transportadora_api.get("results")
            or []
        )

    elif isinstance(resp_transportadora_api, list):
        carriers = resp_transportadora_api

    else:
        carriers = []

    if request.method == "POST":
        ids_texto = (request.POST.get("travels_ids_texto") or "").strip()
        carrier_id = (request.POST.get("carrier_id") or "").strip()
        motorista_id = (request.POST.get("motorista_id") or "").strip()
        motorista_nome = (request.POST.get("motorista_nome") or "").strip()
        observacao = (request.POST.get("motorista_observacao") or "").strip()

        if not ids_texto:
            messages.error(request, "Informe pelo menos um ID de viagem.")
            return redirect("transportes:atribuir_motorista_viagens_manual")

        if not carrier_id:
            messages.error(request, "Selecione uma transportadora.")
            return redirect("transportes:atribuir_motorista_viagens_manual")

        if not motorista_id:
            messages.error(request, "Selecione um motorista válido.")
            return redirect("transportes:atribuir_motorista_viagens_manual")

        try:
            ids_raw = (
                ids_texto
                .replace(",", "\n")
                .replace(";", "\n")
                .replace("|", "\n")
                .split()
            )

            ids_limpos = []

            for item in ids_raw:
                item = str(item).strip()

                if not item:
                    continue

                try:
                    ids_limpos.append(int(item))
                except ValueError:
                    messages.error(request, f"ID inválido encontrado: {item}")
                    return redirect("transportes:atribuir_motorista_viagens_manual")

            ids_limpos = list(dict.fromkeys(ids_limpos))

            if not ids_limpos:
                messages.error(
                    request, "Nenhum ID de viagem válido foi informado.")
                return redirect("transportes:atribuir_motorista_viagens_manual")

            update_driver_payload = [
                {
                    "travels_ids": ids_limpos,
                    "driver_id": int(motorista_id),
                }
            ]

            created_by = request.user.username

            update_driver_url = (
                f"{TRANSP_API_URL}/v2/order_travel/driver/updated"
                f"?created_by={created_by}&carrier_id={carrier_id}"
            )

            update_driver_client = RequestClient(
                method="POST",
                url=update_driver_url,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                request_data=update_driver_payload,
            )

            update_driver_response = update_driver_client.send_api_request()

            if isinstance(update_driver_response, dict) and update_driver_response.get("detail"):
                detail = update_driver_response.get("detail")

                if isinstance(detail, list):
                    detail = " | ".join(str(item) for item in detail)

                messages.error(request, f"Erro ao atrelar motorista: {detail}")
                return redirect("transportes:atribuir_motorista_viagens_manual")

            messages.success(
                request,
                f"Motorista {motorista_nome or motorista_id} vinculado com sucesso a {len(ids_limpos)} viagem(ns)."
            )

            return redirect("transportes:atribuir_motorista_viagens_manual")

        except Exception as e:
            messages.error(request, f"Erro ao atrelar motorista: {e}")
            return redirect("transportes:atribuir_motorista_viagens_manual")

    return render(request, "transportes/transportes/atribuir_motorista.html", {
        "site_title": titulo,
        "current_parent_menu": "transportes",
        "current_menu": "atribuir_motorista",
        "carriers": carriers,
    })
