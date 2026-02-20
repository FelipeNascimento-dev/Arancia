from ...forms import ConsultaOStranspForm
from django.shortcuts import render
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages


def consulta_os_transp(request):
    titulo = 'Consulta OS'
    form = ConsultaOStranspForm(request.GET or None, nome_form=titulo)
    cliente = request.GET.get('client')
    status = request.GET.get('status')

    if not cliente:
        url = f"{TRANSP_API_URL}/gai/list/clientes?cliente=arancia_client"
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

        if 'detail' in resp:
            messages.error(request, resp.get(
                "detail", "Chamado não encontrado!"))

        form.fields['client'].choices = [
            ("", "Todos os clientes")] + [(cliente['id'], cliente['nome']) for cliente in resp]

    return render(request, 'transportes/transportes/consulta_os_transp.html', {
        "form": form,
        "site_title": titulo,
        "botao_texto": "Consultar",
    })
