from django.shortcuts import redirect, render
from setup.local_settings import API_URL
from utils.request import RequestClient
from django.contrib import messages
JSON_CT = "application/json"


def button_desn(request, order: str):
    url = f"{API_URL}/api/v2/trackings/send"
    client = RequestClient(
        url=url,
        method="POST",
        headers={"Accept": JSON_CT},
        request_data={
            "order_number": order,
            "volume_number": 1,
            "order_type": "RETURN",
            "tracking_code": "209"
        }
    )

    result = client.send_api_request()
    if 'detail' not in result:
        request.session['request_success'] = True
        request.session.modified = True
    else:
        request.session['request_success'] = False
        messages.error(request, f"{result['detail']}")

    return redirect('logistica:detalhe_pedido', order=order)
