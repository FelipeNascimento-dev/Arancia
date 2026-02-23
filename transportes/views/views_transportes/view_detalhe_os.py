from django.shortcuts import render
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages


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

    return render(request, 'transportes/transportes/detalhe_os.html', {
        "order_number": order_number,
        "payload": resp
    })
