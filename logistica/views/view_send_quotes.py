from django.shortcuts import render, redirect
from django.contrib import messages
from utils.request import RequestClient
from ..forms import ReverseCreateForm
from setup.local_settings import API_URL

JSON_CT = "application/json"


def send_quotes(request):
    titulo = 'Reversa de Equipamento'
    user_sales_channel = None

    user = request.user
    sales_channel = user.designacao.informacao_adicional.sales_channel
    location_id = 0 if sales_channel == 'all' else user.designacao.informacao_adicional_id
    romaneio_in = request.session.get("romaneio_num", None)
    # to_location_id = request.session.get("group_aditional_information")

    if "enviar_cotacao" in request.POST:
        form = ReverseCreateForm(
            request.POST)
        if form.is_valid():
            to_location_id = form.cleaned_data.get(
                "group_aditional_information")

            payload = {
                "romaneio_number": romaneio_in,
                "from_location_id": location_id,
                "to_location_id": to_location_id,
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
            result = client.send_api_request()

            if "detail" in result:
                messages.error(request, result.get("detail"))
            else:
                request.session["result"] = result
                request.session.modified = True

        return result
