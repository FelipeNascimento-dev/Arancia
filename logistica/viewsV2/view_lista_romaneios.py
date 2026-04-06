from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from logistica.forms.forms_reverse.forms_lista_romaneios import ListaRomaneiosForm
from django.contrib import messages
JSON_CT = "application/json"


def lista_romaneios(request):
    titulo = "Lista de Romaneios"
    form = ListaRomaneiosForm(request.POST or None, nome_form=titulo)

    user = request.user
    sales_channel = user.designacao.informacao_adicional.sales_channel
    location_id = 0 if sales_channel == 'all' else user.designacao.informacao_adicional_id

    result = []
    page_obj = None
    status_rom = ''
    page_number = 1

    if request.method == 'POST':
        status_rom = request.POST.get('status_rom', '')
        page_number = request.POST.get('page', 1)

        if "enviar_evento" in request.POST:
            url = f"{STOCK_API_URL}/v2/romaneios/?location_id={location_id}"

            if status_rom:
                url += f"&status={status_rom}"

            client = RequestClient(
                url=url,
                method="GET",
                headers={
                    "Accept": JSON_CT,
                    "Content-Type": "application/json"
                },
            )
            result = client.send_api_request() or []

            if isinstance(result, dict):
                if 'detail' in result:
                    messages.error(request, result.get('detail'))
                    result = []
                elif 'results' in result and isinstance(result.get('results'), list):
                    result = result.get('results', [])
                elif 'items' in result and isinstance(result.get('items'), list):
                    result = result.get('items', [])
                else:
                    result = []

            if not isinstance(result, list):
                result = []

            for item in result:
                if isinstance(item, dict) and item.get("created_at"):
                    dt = datetime.fromisoformat(item["created_at"])
                    item["created_at_formatado"] = dt.strftime(
                        "%d/%m/%Y %H:%M:%S")

            paginator = Paginator(result, 15)

            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

    return render(request, 'logistica/templatesV2/lista_romaneios.html', {
        'botao_texto': 'Listar',
        'site_title': titulo,
        'form': form,
        'result': result,
        'page_obj': page_obj,
        'status_rom': status_rom,
        "current_parent_menu": "logistica",
        "current_menu": "lastmile",
        "current_submenu": "reverse",
        "current_subsubmenu": "lista_romaneio"
    })
