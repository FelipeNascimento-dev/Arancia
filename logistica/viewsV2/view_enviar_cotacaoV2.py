from django.contrib import messages
from utils.request import RequestClient
from setup.local_settings import API_URL

JSON_CT = "application/json"


def send_quotesV2(request):
    if "enviar_cotacao" in request.POST:
        session_result = request.session.get("result") or {}

        romaneio_in = request.session.get(
            "romaneio_num") or session_result.get("romaneio")
        from_location_id = request.session.get(
            "reverse_origin_id") or session_result.get("origin_id")
        to_location_id = request.session.get(
            "reverse_destination_id") or session_result.get("destination_id")

        if not romaneio_in:
            messages.error(request, "Romaneio não encontrado.")
            return {"detail": "Romaneio não encontrado."}

        if from_location_id in [None, "", "None"]:
            messages.error(request, "Origem não encontrada.")
            return {"detail": "Origem não encontrada."}

        if to_location_id in [None, "", "None"]:
            messages.error(request, "Destino não encontrado.")
            return {"detail": "Destino não encontrado."}

        payload = {
            "romaneio_number": romaneio_in,
            "from_location_id": int(from_location_id),
            "to_location_id": int(to_location_id),
            "created_by": request.user.username if request.user.is_authenticated else "SYSTEM"
        }

        url = f"{API_URL}/api/reverse-order/new/"
        client = RequestClient(
            url=url,
            method="POST",
            headers={
                "Accept": JSON_CT,
                "Content-Type": "application/json"
            },
            request_data=payload,
        )

        print(payload)

        result = client.send_api_request()

        if isinstance(result, dict) and "detail" in result:
            messages.error(request, result.get("detail"))
        else:
            request.session["result"] = result
            request.session.modified = True

        return result
