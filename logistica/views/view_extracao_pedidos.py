from django.http import StreamingHttpResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from ..forms import ExtracaoForm
from utils.request import RequestClient

DEFAULT_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DEFAULT_CD = 'attachment; filename="order_sumary.xlsx"'

def extracao_pedidos(request: HttpRequest) -> HttpResponse:
    # GET com ?download=1 -> retorna o arquivo
    if request.method == "GET" and request.GET.get("download") == "1":
        sales_channel = request.session.get("sales_channel") or "All"

        client = RequestClient(
            url=f"http://192.168.0.216/homo-fulfillment/api/order-sumary/{sales_channel}/xlsx",
            method="GET",
            headers={"Accept": DEFAULT_CT},  # GET -> use Accept (não Content-Type)
        )

        # Simples e seguro: não use streaming aqui
        resp = client.send_api_request_no_json(stream=False)  # httpx.Response

        status = int(getattr(resp, "status_code", 0) or 0)
        if status == 200:
            ct = resp.headers.get("Content-Type", DEFAULT_CT)
            cd = resp.headers.get("Content-Disposition", DEFAULT_CD)
            content = resp.content

            # (opcional) valida se parece um XLSX (arquivo ZIP: começa com PK\x03\x04)
            if not content.startswith(b"PK\x03\x04"):
                messages.error(request, "O servidor retornou um conteúdo inesperado (não parece um XLSX).")
                form = ExtracaoForm(initial={"sales_channel": sales_channel})
                return render(request, "logistica/extracao_pedidos.html", {
                    "form": form,
                    "botao_texto": "Exportar",
                })

            # Retorna o arquivo
            response = HttpResponse(content, content_type=ct)
            response["Content-Disposition"] = cd
            # (opcional) Content-Length se presente
            cl = resp.headers.get("Content-Length")
            if cl:
                response["Content-Length"] = cl
            return response

        # Erro da API → volta ao template com mensagem
        messages.error(request, f"Erro ao baixar (status {status}).")
        form = ExtracaoForm(initial={"sales_channel": sales_channel})
        return render(request, "logistica/extracao_pedidos.html", {
            "form": form,
            "botao_texto": "Exportar",
        })

    # POST -> valida e redireciona para o download na MESMA URL
    if request.method == "POST":
        form = ExtracaoForm(request.POST)
        if form.is_valid():
            sales_channel = form.cleaned_data["sales_channel"]
            request.session["sales_channel"] = sales_channel
            #messages.success(request, "Arquivo gerado com sucesso. O download iniciará em instantes.")
            return redirect(f"{reverse('logistica:extracao_pedidos')}?download=1")
        else:
            messages.error(request, "Corrija os erros do formulário.")
            return render(request, "logistica/extracao_pedidos.html", {
                "form": form,
                "botao_texto": "Exportar",
            })

    # GET normal -> exibe o formulário
    form = ExtracaoForm(initial={"sales_channel": request.session.get("sales_channel")})
    return render(request, "logistica/extracao_pedidos.html", {
        "form": form,
        "botao_texto": "Exportar",
    })
