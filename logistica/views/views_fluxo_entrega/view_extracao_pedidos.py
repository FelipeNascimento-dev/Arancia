from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

from ...forms import ExtracaoForm
from utils.request import RequestClient
from setup.local_settings import API_URL
from ..views_lastmile_consultas.view_consulta_pedidos import get_user_sales_channel


DEFAULT_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DEFAULT_CD = 'attachment; filename="order_sumary.xlsx"'
SESSION_KEY = "extracao_sales_channel"
TEMPLATE = "logistica/templates_fluxo_entrega/extracao_pedidos.html"


def _sales_channel_choices(user):
    sales_channels = [sc for sc in get_user_sales_channel(user) if sc]
    return [(sc, sc) for sc in sales_channels]


def _render_form(request, form):
    return render(request, TEMPLATE, {
        "form": form,
        "botao_texto": "Exportar",
        "site_title": "Extração de Pedidos",
    })


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def extracao_pedidos(request: HttpRequest) -> HttpResponse:
    choices = _sales_channel_choices(request.user)

    if request.method == "GET" and request.GET.get("download") == "1":
        sales_channel = request.session.pop(SESSION_KEY, None)
        form = ExtracaoForm(sales_channel_choices=choices)

        if not sales_channel:
            messages.error(
                request, 'Selecione um canal de vendas para exportar.')
            return _render_form(request, form)

        url = f"{API_URL}/api/order-sumary/{sales_channel}/xlsx"
        client = RequestClient(
            url=url,
            method="GET",
            headers={"Accept": DEFAULT_CT},
        )

        resp = client.send_api_request_no_json(stream=False)

        status = int(getattr(resp, "status_code", 0) or 0)
        if status == 200:
            ct = resp.headers.get("Content-Type", DEFAULT_CT)
            cd = resp.headers.get("Content-Disposition", DEFAULT_CD)
            content = resp.content

            if not content.startswith(b"PK\x03\x04"):
                messages.error(
                    request, "O servidor retornou um conteúdo inesperado.")
                return _render_form(request, form)

            response = HttpResponse(content, content_type=ct)
            response["Content-Disposition"] = cd
            cl = resp.headers.get("Content-Length")
            if cl:
                response["Content-Length"] = cl
            return response

        messages.error(request, f"Erro ao baixar (status {status}).")
        return _render_form(request, form)

    if request.method == "POST":
        form = ExtracaoForm(request.POST, sales_channel_choices=choices)
        if form.is_valid():
            request.session[SESSION_KEY] = form.cleaned_data["sales_channel"]
            return redirect(f"{reverse('logistica:extracao_pedidos')}?download=1")
        messages.warning(request, "Corrija os erros do formulário.")
        return _render_form(request, form)

    if not choices:
        messages.info(
            request, "Nenhum sales_channel disponível para seus grupos.")

    form = ExtracaoForm(sales_channel_choices=choices)
    return _render_form(request, form)
