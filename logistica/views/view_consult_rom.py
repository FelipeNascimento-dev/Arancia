from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import RomaneioConsultaForm
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def consult_rom(request):
    titulo = 'Consultar Romaneio'
    proximo_disponivel = None
    result = None

    if request.method == "POST":
        form = RomaneioConsultaForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero"]

            # 🔎 tenta buscar romaneio
            url_get = f"{STOCK_API_URL}/api/v1/romaneios/{numero}"
            client_get = RequestClient(
                url=url_get, method="GET", headers={"Accept": JSON_CT})
            result_get = client_get.send_api_request()

            # se a API retornou um romaneio válido
            if result_get and isinstance(result_get, dict) and result_get.get("romaneio"):
                request.session["romaneio_num"] = numero
                return redirect("logistica:reverse_create")

            # 🚀 se não existe, cria novo romaneio
            url_post = f"{STOCK_API_URL}/api/v1/romaneios/create"
            payload = {
                "romaneio": numero,
                "status": "ABERTO",
                "volums": []
            }

            client_post = RequestClient(
                url=url_post,
                method="POST",
                headers={"Accept": JSON_CT,
                         "Content-Type": "application/json"},
                request_data=payload,
            )
            result_post = client_post.send_api_request()

            if result_post and isinstance(result_post, dict) and result_post.get("romaneio"):
                result = result_post
                request.session["romaneio_num"] = result.get("romaneio")
                messages.success(
                    request, f"Romaneio {numero} criado com sucesso!")
                return redirect("logistica:reverse_create")
            else:
                messages.error(
                    request, f"Erro ao criar romaneio: {result_post}")

    else:
        form = RomaneioConsultaForm(nome_form=titulo)

    return render(request, "logistica/consult_rom.html", {
        "form": form,
        "botao_texto": 'Consultar',
        "proximo_disponivel": proximo_disponivel,
        "site_title": 'Consulta de Romaneio',
        "result": result,
    })
