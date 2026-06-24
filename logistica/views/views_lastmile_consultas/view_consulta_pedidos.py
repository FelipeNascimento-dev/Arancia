from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.urls import reverse

from setup.local_settings import API_URL
from utils.request import RequestClient
from ...forms import ConsultaPedForm
from ...models import GroupAditionalInformation

PERM_GERENCIAR = "logistica.pode_gerenciar_filiais"
JSON_CT = "application/json"
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500
DEFAULT_SHIPMENT_ORDER_TYPE = "NORMAL"


def get_user_sales_channel(user):
    if not user.has_perm(PERM_GERENCIAR):
        sc = None
        if getattr(user, 'designacao', None) and user.designacao.informacao_adicional:
            gai = user.designacao.informacao_adicional
            if getattr(gai, 'group', None) and gai.group.name == "arancia_PA":
                sc = (gai.sales_channel or "").strip()
        return [sc] if sc else []

    qs = (
        GroupAditionalInformation.objects
        .exclude(sales_channel__isnull=True)
        .exclude(sales_channel__exact="")
        .values_list("sales_channel", flat=True)
        .distinct()
    )

    sales_channels = sorted(
        {(sc or "").strip() for sc in qs if sc},
        key=lambda s: s.lower()
    )
    return sales_channels


def _parse_positive_int(value, default, *, minimum=1, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if parsed < minimum:
        return minimum
    if maximum is not None and parsed > maximum:
        return maximum
    return parsed


def _build_page_range(current_page, total_pages, window=2):
    if total_pages <= 0:
        return []
    start = max(1, current_page - window)
    end = min(total_pages, current_page + window)
    return list(range(start, end + 1))


def _fetch_pedidos_paginados(sales_channel, page, page_size):
    url = f"{API_URL}/api/order-sumary/{sales_channel}/json/v2"
    client = RequestClient(
        url=url,
        method="GET",
        headers={"Accept": JSON_CT},
        request_data={
            "shipment_order_type": DEFAULT_SHIPMENT_ORDER_TYPE,
            "page": page,
            "page_size": page_size,
        },
    )
    result = client.send_api_request()
    if not isinstance(result, dict):
        raise ValueError("Resposta inválida da API.")

    if result.get("detail") and "items" not in result:
        raise ValueError(result.get("detail"))

    current_page = _parse_positive_int(result.get("page"), page)
    current_page_size = _parse_positive_int(
        result.get("page_size"), page_size, maximum=MAX_PAGE_SIZE)
    total_pages = max(0, _parse_positive_int(
        result.get("total_pages"), 0, minimum=0, maximum=10**9))
    has_next = bool(result.get("has_next"))
    has_previous = bool(result.get("has_previous"))

    return {
        "items": result.get("items") or [],
        "paginacao": {
            "total": max(0, _parse_positive_int(
                result.get("total"), 0, minimum=0, maximum=10**9)),
            "page": current_page,
            "page_size": current_page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
            "previous_page": current_page - 1 if has_previous else None,
            "next_page": current_page + 1 if has_next else None,
            "page_range": _build_page_range(current_page, total_pages),
        },
    }


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def consulta_pedidos(request):
    sales_channels = [sc for sc in get_user_sales_channel(request.user) if sc]
    choices = [(sc, sc) for sc in sales_channels]

    tabela_dados = None
    paginacao = None

    if request.method == "POST":
        form = ConsultaPedForm(request.POST, sales_channel_choices=choices)

        if form.is_valid():
            sc = form.cleaned_data["sales_channel"]
            page = _parse_positive_int(request.POST.get("page"), 1)
            page_size = _parse_positive_int(
                request.POST.get("page_size"),
                DEFAULT_PAGE_SIZE,
                maximum=MAX_PAGE_SIZE,
            )

            try:
                resultado = _fetch_pedidos_paginados(sc, page, page_size)
                tabela_dados = resultado["items"]
                paginacao = resultado["paginacao"]

                if not tabela_dados:
                    messages.info(
                        request, "Nenhum registro encontrado para o canal selecionado.")
                else:
                    messages.success(
                        request, f"Consulta realizada para o canal: {sc}")

            except Exception as e:
                tabela_dados = None
                paginacao = None
                messages.error(request, f"Erro ao consultar a API: {e}")
    else:
        form = ConsultaPedForm(sales_channel_choices=choices)

    if not sales_channels:
        messages.info(
            request, "Nenhum sales_channel disponível para seus grupos.")

    return render(request, "logistica/templates_lastmile_consultas/consulta_pedido_extracao.html", {
        "form": form,
        "form_action": reverse("logistica:consulta_pedidos"),
        "botao_texto": "Consultar",
        "site_title": "Consulta de Pedidos",
        "tabela_dados": tabela_dados,
        "paginacao": paginacao,
        "current_parent_menu": "logistica",
        "current_menu": "lastmile",
        "current_submenu": "consultas",
        "current_subsubmenu": "extracao_pedido"
    })
