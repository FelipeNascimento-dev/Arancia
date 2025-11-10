from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from utils.request import RequestClient
from ..forms import ClientConsultForm
from setup.local_settings import STOCK_API_URL
import json

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def client_consult(request):
    titulo = "Consulta de Cliente"
    choices = []

    if request.method == "POST":
        client_code = request.POST.get("client_code")
        client_name = request.POST.get("client_name")
        created_by = request.user.username
        extra_info_raw = request.POST.get("extra_info", "").strip()

        payload = {
            "client_code": client_code,
            "client_name": client_name,
            "created_by": created_by,
        }

        if extra_info_raw:
            try:
                extra_info = json.loads(extra_info_raw)
                if isinstance(extra_info, dict):
                    payload["extra_info"] = extra_info
                else:
                    messages.warning(
                        request,
                        "⚠️ O campo 'Informações Extras' deve ser um JSON de objeto válido (ex: {'endereco': 'Rua X'})."
                    )
                    return redirect("logistica:client_consult")
            except json.JSONDecodeError:
                messages.warning(
                    request,
                    "⚠️ O campo 'Informações Extras' contém um JSON inválido."
                )
                return redirect("logistica:client_consult")

        url = f"{STOCK_API_URL}/v1/clients/"
        headers = {"Content-Type": JSON_CT, "Accept": JSON_CT}

        try:
            res = RequestClient(
                url=url,
                method="POST",
                headers=headers,
                request_data=payload,
            )
            result = res.send_api_request()

            if isinstance(result, dict) and result.get("client_code"):
                messages.success(
                    request, f"Cliente '{client_name}' criado com sucesso!"
                )
            else:
                messages.error(request, f"Erro ao criar cliente: {result}")
        except Exception as e:
            messages.error(request, f"Falha ao criar cliente: {e}")

        return redirect("logistica:client_consult")

    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=100"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        try:
            if isinstance(result, (dict, list)):
                data = result
            elif isinstance(result, (str, bytes)):
                data = json.loads(result)
            elif hasattr(result, "json"):
                data = result.json()
            elif hasattr(result, "text"):
                data = json.loads(result.text)
            else:
                data = []
        except Exception:
            data = []

        if isinstance(data, list) and len(data) > 0:
            choices = [
                (str(i.get("client_code", "")), i.get("client_name", "Sem nome"))
                for i in data
            ]
        else:
            choices = [("", "Nenhum cliente encontrado")]
    except Exception as e:
        messages.error(request, f"Erro ao obter clientes: {e}")
        choices = [("", "Erro ao carregar clientes")]

    form = ClientConsultForm(nome_form=titulo, client_choices=choices)

    return render(
        request,
        "logistica/client_consult.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar Clientes",
        },
    )
