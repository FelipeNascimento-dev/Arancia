from django.shortcuts import render, redirect
from ...forms import ListaViagensForm
from django.contrib import messages
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
import json
import requests
from django.http import JsonResponse

UPLOAD_API_URL = f"http://192.168.0.216/RetencaoAPI/api/v3/upload/upload/Firebase/"


def detalhe_viagem(request, id_viagem):
    titulo = f'Detalhe da Viagem {id_viagem}'

    try:
        id_viagem = int(id_viagem)

        url = f"{TRANSP_API_URL}/order_travels/get_by/arancia/{id_viagem}"
        client = RequestClient(
            method="get",
            url=url,
            headers={"accept": "application/json",
                     "Content-Type": "application/json"},
        )
        resp = client.send_api_request()

        if 'detail' in resp:
            messages.error(request, resp['detail'])

    except Exception:
        pass

    client_id = resp.get("travel", {}).get(
        "order", {}).get("client", {}).get("nome")
    order_type = resp.get("travel", {}).get(
        "order", {}).get("order_type", {}).get("id")

    travel_event_types = []

    url_types = f"{TRANSP_API_URL}/order_events_types/list?status=true&cliente={client_id}&order_type={order_type}"

    response_types = RequestClient(
        method="GET",
        url=url_types,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    response_types = response_types.send_api_request()

    # print(response_types)

    if isinstance(response_types, list):
        travel_event_types = response_types

    if "criar_evento_travel" in request.POST:
        travel_id = int(request.POST.get("travel_id"))
        event_type_id = int(request.POST.get("event_type_id"))
        description = (request.POST.get("description") or "").strip()
        created_by = request.user.username
        location_lat = (request.POST.get("location_lat") or "").strip()
        location_long = (request.POST.get("location_long") or "").strip()

        selected_items = [int(i)
                          for i in request.POST.getlist("items") if i]

        payload_event = {
            "event_type_id": event_type_id,
            "created_by": created_by,
        }

        if description:
            payload_event["description"] = description
        if location_lat:
            payload_event["location_lat"] = location_lat
        if location_long:
            payload_event["location_long"] = location_long
        if selected_items:
            payload_event["extra_information"] = {"items": selected_items}

        file_obj = request.FILES.get("event_image")

        if file_obj and file_obj.size > 0:
            try:
                upload_resp = requests.post(
                    UPLOAD_API_URL,
                    headers={
                        "access_token": "123",
                    },
                    files={
                        "file": (
                            file_obj.name,
                            file_obj,
                            file_obj.content_type or "application/octet-stream"
                        )
                    },
                    timeout=60,
                )

                upload_resp.raise_for_status()

                if "application/json" in upload_resp.headers.get("Content-Type", ""):
                    upload_data = upload_resp.json()
                else:
                    upload_data = upload_resp.text

                if isinstance(upload_data, str):
                    img_url = upload_data.strip().strip('"')
                elif isinstance(upload_data, dict):
                    img_url = upload_data.get(
                        "url") or upload_data.get("data")
                else:
                    img_url = None

                if img_url:
                    payload_event["img_url"] = img_url
                else:
                    messages.error(
                        request, "Upload retornou resposta inválida.")

            except Exception as e:
                messages.error(request, f"Falha ao enviar imagem: {e}")
                return redirect('transportes:detalhe_viagem', id_viagem=id_viagem)

        url = f"{TRANSP_API_URL}/order_tracking_events/create?id={travel_id}&destination=travel"

        client = RequestClient(
            method="POST",
            url=url,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            request_data=payload_event
        )

        print(payload_event)

        response_event = client.send_api_request()

        print(response_event)

        if isinstance(response_event, dict) and "detail" in response_event:
            messages.error(request, response_event["detail"])
        else:
            messages.success(request, "Evento criado com sucesso!")
            return redirect('transportes:detalhe_viagem', id_viagem=id_viagem)

    return render(request, 'transportes/transportes/detalhe_viagem.html', {
        'id_viagem': id_viagem,
        'titulo': titulo,
        'payload': resp,
        "travel_event_types": travel_event_types,
    })
