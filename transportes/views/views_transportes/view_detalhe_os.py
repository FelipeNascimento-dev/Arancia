from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import TRANSP_API_URL, URL_LABEL_INTELIPOST, API_KEY_INTELIPOST
from utils.request import RequestClient
from django.contrib import messages
from django.db.models import Q
from logistica.models import Group, GroupAditionalInformation
import json
import requests
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime


def _get_items_from_response(response):
    if isinstance(response, dict):
        return response.get("items") or response.get("results") or []
    elif isinstance(response, list):
        return response
    return []


def _normalizar_texto(valor):
    return str(valor or "").strip().upper()


def _filtrar_quotes_por_status(quotes):
    quotes_rejeitadas = []
    quotes_aprovadas_unicas = []
    quotes_aprovadas_multiplas = []
    quotes_aprovadas = []
    quotes_pendentes = []

    for quote in quotes:
        status_obj = quote.get("status") or {}

        status_nome = _normalizar_texto(
            status_obj.get("type")
            or status_obj.get("nome")
            or status_obj.get("description")
            or status_obj.get("status")
        )

        if "REJEC" in status_nome:
            quotes_rejeitadas.append(quote)

        elif "APPROV" in status_nome and "ONLY" in status_nome:
            quotes_aprovadas_unicas.append(quote)
            quotes_aprovadas.append(quote)

        elif "APPROV" in status_nome and ("MULT" in status_nome or "MULTIP" in status_nome):
            quotes_aprovadas_multiplas.append(quote)
            quotes_aprovadas.append(quote)

        elif "PEND" in status_nome:
            quotes_pendentes.append(quote)

    return {
        "quotes_rejeitadas": quotes_rejeitadas,
        "quotes_aprovadas_unicas": quotes_aprovadas_unicas,
        "quotes_aprovadas_multiplas": quotes_aprovadas_multiplas,
        "quotes_aprovadas": quotes_aprovadas,
        "quotes_pendentes": quotes_pendentes,
    }


def buscar_motoristas(request):
    nome = request.GET.get("nome", "").strip()
    carrier_id = request.GET.get("carrier_id")

    if not nome:
        return JsonResponse({"items": []})

    url = f"{TRANSP_API_URL}/Carriers/driver/list?Nome={nome}&carrier_id={carrier_id}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {
        "Nome": nome,
        "limit": 10
    }

    if carrier_id:
        params["carrier_id"] = carrier_id

    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
    )

    response_moto = client.send_api_request()

    # print(response_moto)

    items = []
    if isinstance(response_moto, dict):
        items = response_moto.get(
            "items") or response_moto.get("results") or []
    elif isinstance(response_moto, list):
        items = response_moto

    return JsonResponse({"items": items})


def buscar_veiculos(request):

    carrier_id = request.GET.get("carrier_id")
    plate = request.GET.get("plate", "").strip()

    if not carrier_id:
        return JsonResponse({"items": []})

    url = f"{TRANSP_API_URL}/carriers_vehicles/list?plate={plate}&carrier_id={carrier_id}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {
        "carrier_id": carrier_id,
        "limit": 20
    }

    if plate:
        params["plate"] = plate

    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
    )

    response_carros = client.send_api_request()

    items = []
    if isinstance(response_carros, dict):
        items = response_carros.get(
            "items") or response_carros.get("results") or []
    elif isinstance(response_carros, list):
        items = response_carros

    return JsonResponse({"items": items})


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.ver_transportes', raise_exception=True)
def detalhe_os_transp(request, order_number):
    modal_travel_events = False
    modal_confirmacao = False
    confirmation_text = ""
    confirmation_action = ""
    confirmation_id = None
    travel_event_types = []
    travel_items = []

    url = f"{TRANSP_API_URL}/service_orders/{order_number}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
    )

    resp = client.send_api_request()

    quotes_data = resp.get("quotes", []) or []
    quotes_filtradas = _filtrar_quotes_por_status(quotes_data)

    # print(resp)

    def convert_utc_to_local(date_str):
        if not date_str:
            return None
        dt = parse_datetime(date_str)
        if dt:
            return localtime(dt)
        return None

    if resp.get("service_order", {}).get("created_at"):
        resp["service_order"]["created_at"] = convert_utc_to_local(
            resp["service_order"]["created_at"]
        )

    for travel in resp.get("travels", []):
        if travel.get("created_at"):
            travel["created_at"] = convert_utc_to_local(travel["created_at"])

        for ev in travel.get("travel_events", []):
            if ev.get("created_at"):
                ev["created_at"] = convert_utc_to_local(
                    ev["created_at"]
                )

    for event in resp.get("service_order", {}).get("service_order_events", []):
        if event.get("created_at"):
            event["created_at"] = convert_utc_to_local(event["created_at"])

    # print(resp)

    url_carriers = f"{TRANSP_API_URL}/Carriers/list"
    carriers_request = RequestClient(
        method="get",
        url=url_carriers,
        headers=headers
    )
    carriers_resp = carriers_request.send_api_request()

    carriers = []
    if isinstance(carriers_resp, dict):
        carriers = carriers_resp.get(
            "items") or carriers_resp.get("results") or []
    elif isinstance(carriers_resp, list):
        carriers = carriers_resp

    grupos_base = Group.objects.filter(
        Q(name="arancia_PA") |
        Q(name="arancia_CD") |
        Q(name="arancia_CUSTOMER")
    )

    grupos = GroupAditionalInformation.objects.filter(
        group__in=grupos_base
    ).select_related("group").order_by("nome")

    if request.method == "POST":
        if "criar_item" in request.POST:
            def to_float(value):
                if not value:
                    return 0.0
                try:
                    return float(str(value).replace(",", "."))
                except:
                    return 0.0

            ex_order_number = request.POST.get("os_number")
            serial_number = request.POST.get("serial_number")
            product_model = request.POST.get("product_model")
            created_by = request.POST.get("created_by") or "Sistema"
            client_id = resp.get("client", {}).get("id", 0)
            service_order_id = int(request.POST.get("service_order_id") or 0)
            item_control = request.POST.get("item_control")
            item_qtd = int(request.POST.get("item_qtd") or 1)

            weight = to_float(request.POST.get("weight"))
            height = to_float(request.POST.get("height"))
            length = to_float(request.POST.get("length"))
            width = to_float(request.POST.get("width"))

            extra_keys = request.POST.getlist("extra_key[]")
            extra_values = request.POST.getlist("extra_value[]")

            extra_information = {}

            for k, v in zip(extra_keys, extra_values):
                if k:
                    extra_information[k] = v

            sub_qtd = int(request.POST.get("sub_qtd") or 0)
            sub_serials = request.POST.getlist("sub_serial[]")
            sub_models = request.POST.getlist("sub_model[]")
            sub_types = request.POST.getlist("sub_type[]")
            sub_controls = request.POST.getlist("sub_control[]")
            sub_weights = request.POST.getlist("sub_weight[]")
            sub_heights = request.POST.getlist("sub_height[]")
            sub_lengths = request.POST.getlist("sub_length[]")
            sub_widths = request.POST.getlist("sub_width[]")

            sub_itens = []

            for i in range(len(sub_serials)):

                if not sub_serials[i] and not sub_models[i]:
                    continue

                sub_itens.append({
                    "serial_number": sub_serials[i],
                    "product_model": sub_models[i],
                    "product_type": sub_types[i],
                    "item_control": sub_controls[i],
                    "weight": to_float(sub_weights[i]),
                    "height": to_float(sub_heights[i]),
                    "length": to_float(sub_lengths[i]),
                    "width": to_float(sub_widths[i]),
                    "extra_information": {}
                })

            if sub_qtd > 0:

                for i in range(sub_qtd):

                    sub_itens.append({
                        "serial_number": f"{serial_number}-{i+1}",
                        "product_model": product_model,
                        "product_type": product_model,
                        "item_control": f"{item_control}-{i+1}" if item_control else "",
                        "weight": weight,
                        "height": height,
                        "length": length,
                        "width": width,
                        "extra_information": {
                            "gerado_em_massa": True,
                            "index": i + 1
                        }
                    })

            erro = False

            for i in range(item_qtd):

                serial_loop = serial_number
                control_loop = item_control

                if item_qtd > 1:
                    serial_loop = f"{serial_number}-{i+1}"

                    if item_control:
                        control_loop = f"{item_control}-{i+1}"

                payload_item = {
                    "external_order_number": ex_order_number,
                    "serial_number": serial_loop,
                    "product_model": product_model,
                    "created_by": created_by,
                    "client_id": client_id,
                    "service_order_id": service_order_id,
                    "item_control": control_loop,
                    "weight": weight,
                    "height": height,
                    "length": length,
                    "width": width,
                    "extra_information": extra_information,
                    "sub_itens": sub_itens
                }

                try:

                    url_quote = f"{TRANSP_API_URL}/item/create"

                    client = RequestClient(
                        method="POST",
                        url=url_quote,
                        headers={
                            "accept": "application/json",
                            "Content-Type": "application/json",
                        },
                        request_data=payload_item
                    )

                    item_res = client.send_api_request()

                    # print(payload_item)

                    if isinstance(item_res, dict) and "detail" in item_res:
                        messages.error(request, item_res["detail"])
                        erro = True
                        break

                except Exception as e:
                    messages.error(request, str(e))
                    erro = True
                    break

            if not erro:
                messages.success(
                    request, f"{item_qtd} itens criados com sucesso")

            return redirect(
                "transportes:detalhe_os_transp",
                order_number=order_number
            )

        if "criar_cotacao" in request.POST:
            service_order_id = request.POST.get("service_order_id")
            carrier_id = request.POST.get("carrier_id")
            origin_id = request.POST.get("origin_id")
            destination_id = request.POST.get("destination_id")
            estimated_deadline = request.POST.get("estimated_deadline")
            created_by = request.user.username

            def to_float(value, field_name):
                if not value:
                    return 0.0
                try:
                    return float(str(value).replace(",", "."))
                except ValueError:
                    messages.error(
                        request, f"Valor inválido para {field_name}.")
                    return 0.0

            total_weight = to_float(
                request.POST.get("total_weight"), "Peso Total")
            total_volume = to_float(request.POST.get(
                "total_volume"), "Volume Total")
            estimated_price = to_float(request.POST.get(
                "estimated_price"), "Valor Estimado")

            try:
                url_quote = f"{TRANSP_API_URL}/quotes/create"
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }

                client = RequestClient(
                    method="POST",
                    url=url_quote,
                    headers=headers,
                    request_data={
                        "service_order_id": service_order_id,
                        "carrier_id": carrier_id,
                        "origin_id": origin_id,
                        "destination_id": destination_id,
                        "total_weight": total_weight,
                        "total_volume": total_volume,
                        "estimated_price": estimated_price,
                        "estimated_deadline": estimated_deadline,
                        "created_by": created_by
                    }
                )

                api_response = client.send_api_request()

                # print(client.request_data)

                if 'detail' in api_response:
                    messages.error(request, api_response['detail'])
                else:
                    messages.success(request, "Cotação criada com sucesso!")
                    return redirect('transportes:detalhe_os_transp', order_number=order_number)
            except Exception as e:
                messages.error(request, f"Erro ao criar cotação: {e}")

        if "criar_viagem" in request.POST:
            order_id = int(request.POST.get("service_order_id"))
            driver_id = int(request.POST.get("driver_id"))
            carrier_id = int(request.POST.get("carrier_id"))
            vehicle_id = int(request.POST.get("vehicle_id"))

            quote_id_raw = request.POST.get("quote_id")
            quote_id = int(quote_id_raw) if quote_id_raw else None

            price_charged_raw = request.POST.get("price_charged")

            try:
                price_charged = float(str(price_charged_raw).replace(",", "."))
            except:
                price_charged = 0.0

            created_by = request.user.username

            items = request.POST.getlist("items")
            items = [int(i) for i in items]

            payload_travel = {
                "order_id": order_id,
                "driver_id": driver_id,
                "carrier_id": carrier_id,
                "price_charged": price_charged,
                "vehicle_id": vehicle_id,
                "quote_id": quote_id,
                "created_by": created_by,
                "items": items
            }

            # print(payload_travel)

            try:
                url = f"{TRANSP_API_URL}/order_travels/create"

                client = RequestClient(
                    method="POST",
                    url=url,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    request_data=payload_travel
                )

                response_travel = client.send_api_request()

                if "detail" in response_travel:
                    messages.error(request, response_travel["detail"])
                else:
                    messages.success(request, "Viagem criada com sucesso!")
                    return redirect('transportes:detalhe_os_transp', order_number=order_number)

            except Exception as e:
                messages.error(request, f"Erro ao criar viagem: {e}")

        if "travel_events" in request.POST:
            modal_travel_events = True

            travel_id = request.POST.get("travel_id")

            travel_items = []

            if travel_id:
                travel_items = [
                    item for item in resp.get("items", [])
                    if str(item.get("travel_order_id")) == str(travel_id)
                ]

                client_id = resp.get("client", {}).get("nome")
                order_type = resp.get("service_order", {}).get(
                    "order_type", {}).get("id")
            try:
                url = f"{TRANSP_API_URL}/order_events_types/list?status=true&cliente={client_id}&order_type={order_type}"

                client = RequestClient(
                    method="GET",
                    url=url,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )

                response_travel = client.send_api_request()

                if isinstance(response_travel, list):
                    travel_event_types = [
                        ev for ev in response_travel
                        if ev.get("active") is True
                    ]

                elif isinstance(response_travel, dict) and "detail" in response_travel:
                    messages.error(request, response_travel["detail"])

            except Exception as e:
                messages.error(request, f"Erro ao consultar eventos: {e}")

        if "travel_events_bulk" in request.POST:
            modal_travel_events = True

            travel_ids = request.POST.getlist("travel_ids")
            travel_ids = [str(i) for i in travel_ids if str(i).strip()]

            travel_items = []

            if travel_ids:
                travel_items = [
                    item for item in resp.get("items", [])
                    if str(item.get("travel_order_id")) in travel_ids
                ]

            client_id = resp.get("client", {}).get("nome")
            order_type = resp.get("service_order", {}).get(
                "order_type", {}).get("id")

            try:
                url = f"{TRANSP_API_URL}/order_events_types/list?status=true&cliente={client_id}&order_type={order_type}"

                client = RequestClient(
                    method="GET",
                    url=url,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )

                response_travel = client.send_api_request()

                if isinstance(response_travel, list):
                    travel_event_types = [
                        ev for ev in response_travel
                        if ev.get("active") is True
                    ]

                elif isinstance(response_travel, dict) and "detail" in response_travel:
                    messages.error(request, response_travel["detail"])

            except Exception as e:
                messages.error(request, f"Erro ao consultar eventos: {e}")

        UPLOAD_API_URL = f"http://192.168.0.216/RetencaoAPI/api/v3/upload/upload/Firebase/"

        if "criar_evento_travel" in request.POST:
            travel_id_raw = request.POST.get("travel_id")
            travel_ids = request.POST.getlist("travel_ids")

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
                payload_event["extra_information"] = {
                    "items": selected_items
                }

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
                        return redirect("transportes:detalhe_os_transp", order_number=order_number)

                except Exception as e:
                    messages.error(request, f"Falha ao enviar imagem: {e}")
                    return redirect("transportes:detalhe_os_transp", order_number=order_number)

            try:
                headers_api = {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }

                # fluxo em lote
                if travel_ids:
                    ids_limpos = [str(i) for i in travel_ids if str(i).strip()]

                    query_ids = "&".join([f"ids={i}" for i in ids_limpos])
                    url = f"{TRANSP_API_URL}/v2/order_tracking/create?destination=travel&{query_ids}"

                    client = RequestClient(
                        method="POST",
                        url=url,
                        headers=headers_api,
                        request_data=payload_event
                    )

                    response_event = client.send_api_request()

                # fluxo individual
                else:
                    travel_id = int(travel_id_raw)

                    url = f"{TRANSP_API_URL}/order_tracking_events/create?id={travel_id}&destination=travel"

                    client = RequestClient(
                        method="POST",
                        url=url,
                        headers=headers_api,
                        request_data=payload_event
                    )

                    response_event = client.send_api_request()

                if isinstance(response_event, dict) and "detail" in response_event:
                    messages.error(request, response_event["detail"])
                else:
                    messages.success(request, "Evento criado com sucesso!")
                    return redirect("transportes:detalhe_os_transp", order_number=order_number)

            except Exception as e:
                messages.error(request, f"Erro ao criar evento: {e}")

        if "editar_item" in request.POST:
            def to_float(value):
                if value in (None, ""):
                    return 0.0
                try:
                    return float(str(value).replace(",", "."))
                except:
                    return 0.0

            item_id = request.POST.get("item_id")
            created_by = request.user.username

            serial_number = (request.POST.get("serial_number") or "").strip()
            product_model = (request.POST.get("product_model") or "").strip()
            item_control = (request.POST.get("item_control") or "").strip()
            weight = to_float(request.POST.get("weight"))
            height = to_float(request.POST.get("height"))
            length = to_float(request.POST.get("length"))
            width = to_float(request.POST.get("width"))

            original_serial_number = (request.POST.get(
                "original_serial_number") or "").strip()
            original_product_model = (request.POST.get(
                "original_product_model") or "").strip()
            original_item_control = (request.POST.get(
                "original_item_control") or "").strip()
            original_weight = to_float(request.POST.get("original_weight"))
            original_height = to_float(request.POST.get("original_height"))
            original_length = to_float(request.POST.get("original_length"))
            original_width = to_float(request.POST.get("original_width"))

            payload_update = {}

            if serial_number != original_serial_number:
                payload_update["serial_number"] = serial_number

            if product_model != original_product_model:
                payload_update["product_model"] = product_model

            if item_control != original_item_control:
                payload_update["item_control"] = item_control

            if weight != original_weight:
                payload_update["weight"] = weight

            if height != original_height:
                payload_update["height"] = height

            if length != original_length:
                payload_update["length"] = length

            if width != original_width:
                payload_update["width"] = width

            if not payload_update:
                messages.warning(
                    request, "Nenhuma alteração foi feita no item.")
                return redirect("transportes:detalhe_os_transp", order_number=order_number)

            try:
                url_update = f"{TRANSP_API_URL}/item/update/item?id={item_id}&created_by={created_by}"

                client = RequestClient(
                    method="PUT",
                    url=url_update,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    request_data=payload_update
                )

                update_resp = client.send_api_request()

                if isinstance(update_resp, dict) and "detail" in update_resp:
                    messages.error(request, update_resp["detail"])
                else:
                    messages.success(request, "Item atualizado com sucesso!")
                    return redirect("transportes:detalhe_os_transp", order_number=order_number)

            except Exception as e:
                messages.error(request, f"Erro ao atualizar item: {e}")

        if "editar_viagem" in request.POST:
            def to_float(value):
                if not value:
                    return 0.0
                try:
                    return float(str(value).replace(",", "."))
                except:
                    return 0.0

            travel_id = request.POST.get("travel_id")
            created_by = request.user.username

            driver_id = int(request.POST.get("driver_id") or 0)
            carrier_id = int(request.POST.get("carrier_id") or 0)
            vehicle_id = int(request.POST.get("vehicle_id") or 0)
            quote_id = int(request.POST.get("quote_id") or 0)
            price_charged = to_float(request.POST.get("price_charged"))

            payload_update = {
                "driver_id": driver_id,
                "carrier_id": carrier_id,
                "vehicle_id": vehicle_id,
                "quote_id": quote_id,
                "price_charged": price_charged
            }

            try:
                url_update = f"{TRANSP_API_URL}/order_travels/update/Travel?id={travel_id}&created_by={created_by}"

                client = RequestClient(
                    method="PUT",
                    url=url_update,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    request_data=payload_update
                )

                response_update = client.send_api_request()

                if isinstance(response_update, dict) and "detail" in response_update:
                    messages.error(request, response_update["detail"])
                else:
                    messages.success(
                        request, "Viagem atualizada com sucesso!")
                    return redirect("transportes:detalhe_os_transp", order_number=order_number)

            except Exception as e:
                messages.error(request, f"Erro ao atualizar viagem: {e}")

        if "atrelar_motorista_viagens" in request.POST:
            driver_id = request.POST.get("driver_id")
            carrier_id = request.POST.get("carrier_id")
            travel_ids = request.POST.getlist("travel_ids")

            created_by = request.user.username

            update_driver_payload = [
                {
                    "travels_ids": [int(i) for i in travel_ids],
                    "driver_id": int(driver_id)
                }
            ]

            try:
                update_driver_url = f"{TRANSP_API_URL}/v2/order_travel/driver/updated?created_by={created_by}"

                update_driver_client = RequestClient(
                    method="POST",
                    url=update_driver_url,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    request_data=update_driver_payload
                )

                print(update_driver_payload)

                update_driver_response = update_driver_client.send_api_request()

                if 'detail' in update_driver_response:
                    messages.error(
                        request, update_driver_response.get('detail'))
                else:
                    messages.success(
                        request, "Viagens atualizadas com sucesso!")
                    return redirect("transportes:detalhe_os_transp", order_number=order_number)
            except Exception as e:
                messages.error(request, f"Erro ao consultar eventos: {e}")

        if "editar_cotacao" in request.POST:
            def to_float(value):
                if not value:
                    return 0.0
                try:
                    return float(str(value).replace(",", "."))
                except:
                    return 0.0

            def to_int(value):
                if not value:
                    return 0
                try:
                    return int(value)
                except:
                    return 0

            quote_id = request.POST.get("quote_id")
            carrier_id = to_int(request.POST.get("carrier_id"))
            total_weight = to_float(request.POST.get("total_weight"))
            total_volume = to_float(request.POST.get("total_volume"))
            estimated_price = to_float(request.POST.get("estimated_price"))
            estimated_deadline = to_int(request.POST.get("estimated_deadline"))
            status = (request.POST.get("status") or "").strip()

            payload_update_quote = {
                "carrier_id": carrier_id,
                "total_weight": total_weight,
                "total_volume": total_volume,
                "estimated_price": estimated_price,
                "estimated_deadline": estimated_deadline,
                "status": status,
            }

            print(payload_update_quote)

            try:
                url_update_quote = f"{TRANSP_API_URL}/quotes/update/cotacao?id={quote_id}"

                update_quote_client = RequestClient(
                    method="PUT",
                    url=url_update_quote,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    request_data=payload_update_quote
                )

                response_update_quote = update_quote_client.send_api_request()

                if isinstance(response_update_quote, dict) and "detail" in response_update_quote:
                    messages.error(request, response_update_quote["detail"])
                else:
                    messages.success(
                        request, "Cotação atualizada com sucesso!")
                    return redirect("transportes:detalhe_os_transp", order_number=order_number)

            except Exception as e:
                messages.error(request, f"Erro ao atualizar cotação: {e}")

        if "reject_button" in request.POST:
            quote_id = request.POST.get("quote_id")
            modal_confirmacao = True
            request.session["confirm_action"] = "reject_quote"
            request.session["confirm_id"] = request.POST.get("quote_id")
            request.session["confirm_text"] = "REJEITAR"

        if "delete_item" in request.POST:
            modal_confirmacao = True
            request.session["confirm_action"] = "delete_item"
            request.session["confirm_id"] = request.POST.get("delete_item")
            request.session["confirm_text"] = "DELETAR"

        if "cancel_travel_button" in request.POST:
            modal_confirmacao = True
            request.session["confirm_action"] = "delete_travel"
            request.session["confirm_id"] = request.POST.get(
                "cancel_travel_id")
            request.session["confirm_text"] = "DELETAR"

        if "confirm_action" in request.POST:

            text = request.POST.get("confirm_text")

            action = request.session.get("confirm_action")
            obj_id = request.session.get("confirm_id")
            expected = request.session.get("confirm_text")

            if text != expected:

                modal_confirmacao = True

            else:

                try:

                    if action == "reject_quote":

                        url_reject = f"{TRANSP_API_URL}/quotes/Rejeitar/cotacao?id={obj_id}"

                        cliente_reject = RequestClient(
                            method="PUT",
                            url=url_reject,
                            headers={
                                "accept": "application/json",
                                "Content-Type": "application/json",
                            },
                        )

                        reject_resp = cliente_reject.send_api_request()

                        if isinstance(reject_resp, dict) and "detail" in reject_resp:
                            messages.error(request, reject_resp["detail"])
                        else:
                            messages.success(
                                request,
                                "Cotação rejeitada com sucesso!"
                            )

                            request.session.pop("confirm_action", None)
                            request.session.pop("confirm_id", None)
                            request.session.pop("confirm_text", None)

                            return redirect("transportes:detalhe_os_transp", order_number=order_number)

                    elif action == "delete_travel":
                        url_cancel = f"{TRANSP_API_URL}/order_travels/delete/travel?id={obj_id}&created_by={request.user.username}"

                        cliente_cancel = RequestClient(
                            method="DELETE",
                            url=url_cancel,
                            headers={
                                "accept": "application/json",
                                "Content-Type": "application/json",
                            },
                        )

                        cancel_resp = cliente_cancel.send_api_request()

                        if isinstance(cancel_resp, dict) and "detail" in cancel_resp:
                            messages.error(request, cancel_resp["detail"])
                        else:
                            messages.success(
                                request, "Viagem cancelada com sucesso!")

                            request.session.pop("confirm_action", None)
                            request.session.pop("confirm_id", None)
                            request.session.pop("confirm_text", None)

                            return redirect("transportes:detalhe_os_transp", order_number=order_number)

                    elif action == "delete_item":
                        url_delete = f"{TRANSP_API_URL}/item/{obj_id}"
                        cliente_delete = RequestClient(
                            method="DELETE",
                            url=url_delete,
                            headers={
                                "accept": "application/json",
                                "Content-Type": "application/json",
                            },
                        )
                        delete_resp = cliente_delete.send_api_request()
                        if isinstance(delete_resp, dict) and "detail" in delete_resp:
                            messages.error(request, delete_resp["detail"])
                        else:
                            messages.success(
                                request, "Item deletado com sucesso!")

                            request.session.pop("confirm_action", None)
                            request.session.pop("confirm_id", None)
                            request.session.pop("confirm_text", None)

                            return redirect("transportes:detalhe_os_transp", order_number=order_number)

                except Exception as e:
                    messages.error(request, str(e))
                    modal_confirmacao = True

        if "consultar_etiqueta" in request.POST:
            order_number = request.POST.get("order_number")
            vol_id = request.POST.get("vol_id")

            try:
                url_ip = f"{URL_LABEL_INTELIPOST}{order_number}/{vol_id}"

                client = RequestClient(
                    method="GET",
                    url=url_ip,
                    headers={
                        'Content-Type': 'application/json',
                        'api-key': API_KEY_INTELIPOST
                    })

                response_ip = client.send_api_request()

                if "detail" in response_ip:
                    messages.error(request, response_ip.get("detail"))
                else:
                    messages.success(
                        request, "Etiquetas consultadas com sucesso!")
                    export_url = response_ip['content']['label_url']
                    return redirect(export_url)

            except Exception as e:
                messages.error(request, f"Erro ao consultar etiquetas: {e}")

    confirmation_text = request.session.get("confirm_text")

    if request.method == "POST" and request.POST.get("reject_button"):
        modal_confirmacao = True

    itens_sem_viagem = []

    try:
        service_order_id = resp.get("service_order", {}).get("id")

        if service_order_id:
            url_itens_sem_viagem = (
                f"{TRANSP_API_URL}/item/list"
                f"?service_order_id={service_order_id}"
                f"&sem_travel_order=true"
            )

            client_items_free = RequestClient(
                method="GET",
                url=url_itens_sem_viagem,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

            resp_items_free = client_items_free.send_api_request()

            if isinstance(resp_items_free, dict):
                itens_sem_viagem = (
                    resp_items_free.get("items")
                    or resp_items_free.get("results")
                    or []
                )
            elif isinstance(resp_items_free, list):
                itens_sem_viagem = resp_items_free

    except Exception as e:
        messages.warning(
            request, f"Não foi possível carregar itens livres: {e}")

    selected_travel_ids = []
    if request.method == "POST":
        selected_travel_ids = request.POST.getlist("travel_ids")

    return render(request, 'transportes/transportes/detalhe_os.html', {
        "order_number": order_number,
        "payload": resp,
        "carriers": carriers,
        "grupos": grupos,
        "modal_travel_events": modal_travel_events,
        "travel_event_types": travel_event_types,
        "modal_confirmacao": modal_confirmacao,
        "confirmation_text": confirmation_text,
        "travel_items": travel_items,
        "itens_sem_viagem": itens_sem_viagem,
        "quotes_rejeitadas": quotes_filtradas["quotes_rejeitadas"],
        "quotes_aprovadas_unicas": quotes_filtradas["quotes_aprovadas_unicas"],
        "quotes_aprovadas_multiplas": quotes_filtradas["quotes_aprovadas_multiplas"],
        "quotes_aprovadas": quotes_filtradas["quotes_aprovadas"],
        "quotes_pendentes": quotes_filtradas["quotes_pendentes"],
        "site_title": "Detalhe da OS",
        "current_parent_menu": "transportes",
        "current_menu": "lista_os",
        "selected_travel_ids": selected_travel_ids,
    })
