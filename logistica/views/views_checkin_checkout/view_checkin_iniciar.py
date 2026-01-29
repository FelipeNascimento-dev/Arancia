from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from ...forms import ClientSelectForm
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
import json

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.checkin_principal', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def client_select(request, vetor):
    titulo = "Seleção de Cliente"

    request.session["vetor"] = vetor.upper()

    context = {
        "site_title": titulo,
        "botao_texto": "Selecionar Cliente",
        "current_parent_menu": "logistica",
    }

    if vetor == "IN":
        context.update({
            "current_menu": "checkin",
            "current_submenu": "iniciar_checkin",
        })
    elif vetor == "OUT":
        context.update({
            "current_menu": "checkout",
            "current_submenu": "iniciar_checkout",
        })

    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=1000"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        if isinstance(result, (dict, list)):
            data = result
        else:
            data = json.loads(result)

        choices = [
            (str(i.get("client_code", "")), i.get("client_name", "Sem nome"))
            for i in data
        ] if isinstance(data, list) else []

    except Exception as e:
        messages.error(request, f"Erro ao obter clientes: {e}")
        choices = []

    form = ClientSelectForm(request.POST or None,
                            nome_form=titulo, client_choices=choices)

    if request.method == "POST" and form.is_valid():
        client = form.cleaned_data["client"]
        client_name_real = next(
            (name for code, name in choices if code == client),
            client
        )

        request.session["selected_client"] = {
            "client_code": client,
            "client_name": client_name_real,
        }

        if client.lower() == "cielo":
            if vetor.upper() == "IN":
                return redirect("logistica:client_checkin")

            if vetor.upper() == "OUT":
                return redirect("logistica:checkout_reverse", vetor=vetor)

        if vetor.upper() == "IN":
            return redirect("logistica:client_checkin")

        return redirect("logistica:checkout_reverse", vetor=vetor)

    context["form"] = form

    return render(
        request,
        "logistica/templates_checkin_checkout/checkin_iniciar.html",
        context
    )
