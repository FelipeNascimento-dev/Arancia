from django.shortcuts import render, redirect
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages
from django.db.models import Q
from logistica.models import Group, GroupAditionalInformation
import json
from django.http import JsonResponse


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


def detalhe_os_transp(request, order_number):

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

    return render(request, 'transportes/transportes/detalhe_os.html', {
        "order_number": order_number,
        "payload": resp,
        "carriers": carriers,
        "grupos": grupos,
        "site_title": "Detalhe da OS"
    })
