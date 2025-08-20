from django.http import StreamingHttpResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

from ..models import GroupAditionalInformation
from ..forms import ExtracaoForm
from utils.request import RequestClient
from django.contrib.auth.models import User
from setup.local_settings import API_URL


DEFAULT_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DEFAULT_CD = 'attachment; filename="order_sumary.xlsx"'


def get_user_sales_channel(user: User):
    # Pega todos os sales_channel dos grupos que o usuário pertence
    qs = (
        GroupAditionalInformation.objects
        .filter(group__user=user)                # pega só os grupos desse usuário
        .exclude(sales_channel__isnull=True)     # ignora nulos
        .exclude(sales_channel__exact="")        # ignora vazios
        .values_list("sales_channel", flat=True)
        .distinct()
    )

    sales_channels = list(qs)

    if not sales_channels:
        return None   # usuário sem sales_channel
    return sales_channels[0] 


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def extracao_pedidos(request: HttpRequest) -> HttpResponse:
    if request.method == "GET" and request.GET.get("download") == "1":
        #sales_channel = request.session.get("sales_channel") or "All"
        sales_channel = get_user_sales_channel(request.user)

        if not sales_channel:
            messages.error(request,'Usuário não tem nenhum sales_channel atribuído')
            return render(request, "logistica/extracao_pedidos.html", {
                    "form": form,
                    "botao_texto": "Exportar",
                })

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
                #form = ExtracaoForm(initial={"sales_channel": sales_channel})
                form = ExtracaoForm()
                return render(request, "logistica/extracao_pedidos.html", {
                    "form": form,
                    "botao_texto": "Exportar",
                })

            response = HttpResponse(content, content_type=ct)
            response["Content-Disposition"] = cd
            cl = resp.headers.get("Content-Length")
            if cl:
                response["Content-Length"] = cl
            return response

        messages.error(request, f"Erro ao baixar (status {status}).")
        #form = ExtracaoForm(initial={"sales_channel": sales_channel})
        form = ExtracaoForm()
        return render(request, "logistica/extracao_pedidos.html", {
            "form": form,
            "botao_texto": "Exportar",
        })

    if request.method == "POST":
        form = ExtracaoForm(request.POST)
        if form.is_valid():
            # sales_channel = form.cleaned_data["sales_channel"]
            # request.session["sales_channel"] = sales_channel
            sales_channel = 'all'
            return redirect(f"{reverse('logistica:extracao_pedidos')}?download=1")
        else:
            messages.warning(request, "Corrija os erros do formulário.")
            return render(request, "logistica/extracao_pedidos.html", {
                "form": form,
                "botao_texto": "Exportar",
            })

    #form = ExtracaoForm(initial={"sales_channel": request.session.get("sales_channel")})
    form = ExtracaoForm()
    return render(request, "logistica/extracao_pedidos.html", {
        "form": form,
        "botao_texto": "Exportar",
    })