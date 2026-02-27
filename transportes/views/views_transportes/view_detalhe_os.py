from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages
from django.db.models import Q
from logistica.models import Group, GroupAditionalInformation
import json
import requests
from django.http import JsonResponse


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
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

    response = client.send_api_request()

    print(response)

    items = []
    if isinstance(response, dict):
        items = response.get("items") or response.get("results") or []
    elif isinstance(response, list):
        items = response

    return JsonResponse({"items": items})


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
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

    response = client.send_api_request()

    items = []
    if isinstance(response, dict):
        items = response.get("items") or response.get("results") or []
    elif isinstance(response, list):
        items = response

    return JsonResponse({"items": items})


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def detalhe_os_transp(request, order_number):
    modal_travel_events = False
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

            ex_order_number = request.POST.get("order_number")
            serial_number = request.POST.get("serial_number")
            product_model = request.POST.get("product_model")
            created_by = request.POST.get("created_by") or "Sistema"
            client_id = int(request.POST.get("client_id") or 0)
            service_order_id = int(request.POST.get("service_order_id") or 0)
            item_control = request.POST.get("item_control")

            weight = to_float(request.POST.get("weight"))
            height = to_float(request.POST.get("height"))
            length = to_float(request.POST.get("length"))
            width = to_float(request.POST.get("width"))

            extra_raw = request.POST.get("extra_information", "").strip()
            if extra_raw:
                try:
                    extra_information = json.loads(extra_raw)
                except json.JSONDecodeError:
                    messages.error(
                        request, "Extra Information precisa ser JSON válido.")
                    return redirect('transportes:detalhe_os_transp', order_number=order_number)
            else:
                extra_information = {}

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

            payload = {
                "order_number": ex_order_number,
                "serial_number": serial_number,
                "product_model": product_model,
                "created_by": created_by,
                "client_id": client_id,
                "service_order_id": service_order_id,
                "item_control": item_control,
                "weight": weight,
                "height": height,
                "length": length,
                "width": width,
                "extra_information": extra_information,
                "sub_itens": sub_itens
            }

            try:
                url_quote = f"{TRANSP_API_URL}/item/create"
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }

                client = RequestClient(
                    method="POST",
                    url=url_quote,
                    headers=headers,
                    request_data=payload
                )

                item_res = client.send_api_request()

                print(client.request_data)

                if 'detail' in item_res:
                    messages.error(request, item_res['detail'])
                else:
                    messages.success(request, "Item criado com sucesso!")
                    return redirect('transportes:detalhe_os_transp', order_number=order_number)
            except Exception as e:
                messages.error(request, f"Erro ao criar cotação: {e}")

            return redirect('transportes:detalhe_os_transp', order_number=order_number)

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

                print(client.request_data)

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

            payload = {
                "order_id": order_id,
                "driver_id": driver_id,
                "carrier_id": carrier_id,
                "price_charged": price_charged,
                "vehicle_id": vehicle_id,
                "quote_id": quote_id,
                "created_by": created_by,
                "items": items
            }

            print(payload)

            try:
                url = f"{TRANSP_API_URL}/order_travels/create"

                client = RequestClient(
                    method="POST",
                    url=url,
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    request_data=payload
                )

                response = client.send_api_request()

                if "detail" in response:
                    messages.error(request, response["detail"])
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
                url = f"{TRANSP_API_URL}/order_events_types/list?cliente={client_id}&order_type={order_type}"

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
            travel_id = int(request.POST.get("travel_id"))
            event_type_id = int(request.POST.get("event_type_id"))
            description = (request.POST.get("description") or "").strip()
            created_by = request.user.username
            location_lat = (request.POST.get("location_lat") or "").strip()
            location_long = (request.POST.get("location_long") or "").strip()

            selected_items = [int(i)
                              for i in request.POST.getlist("items") if i]

            payload = {
                "event_type_id": event_type_id,
                "created_by": created_by,
            }

            if description:
                payload["description"] = description
            if location_lat:
                payload["location_lat"] = location_lat
            if location_long:
                payload["location_long"] = location_long
            if selected_items:
                payload["extra_information"] = {"items": selected_items}

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
                        payload["img_url"] = img_url
                    else:
                        messages.error(
                            request, "Upload retornou resposta inválida.")

                except Exception as e:
                    messages.error(request, f"Falha ao enviar imagem: {e}")
                    return redirect('transportes:detalhe_os_transp', order_number=order_number)

            url = f"{TRANSP_API_URL}/order_tracking_events/create?id={travel_id}&destination=travel"

            client = RequestClient(
                method="POST",
                url=url,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                request_data=payload
            )

            response_event = client.send_api_request()

            if isinstance(response_event, dict) and "detail" in response_event:
                messages.error(request, response_event["detail"])
            else:
                messages.success(request, "Evento criado com sucesso!")
                return redirect('transportes:detalhe_os_transp', order_number=order_number)

    return render(request, 'transportes/transportes/detalhe_os.html', {
        "order_number": order_number,
        "payload": resp,
        "carriers": carriers,
        "grupos": grupos,
        "modal_travel_events": modal_travel_events,
        "travel_event_types": travel_event_types,
        "travel_items": travel_items,
        "site_title": "Detalhe da OS"
    })
