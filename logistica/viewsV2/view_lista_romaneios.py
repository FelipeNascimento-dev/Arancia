from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from logistica.forms.forms_reverse.forms_lista_romaneios import ListaRomaneiosForm

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
    })
