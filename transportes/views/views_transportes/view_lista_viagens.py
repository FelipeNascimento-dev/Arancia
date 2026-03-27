from django.shortcuts import render, redirect
from ...forms import ListaViagensForm
from setup.local_settings import TRANSP_API_URL
from django.contrib import messages
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from datetime import datetime
from urllib.parse import urlencode
from django.http import JsonResponse
from datetime import datetime


def formatar_data(data_str, com_hora=True):
    if not data_str or data_str == "None":
        return None

    try:
        dt = datetime.fromisoformat(str(data_str).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")
    except Exception:
        return data_str


def buscar_motoristas_travels(request):
    nome = request.GET.get("nome", "").strip()
    carrier_id = request.GET.get("carrier_id", "").strip()

    if not nome:
        return JsonResponse({"items": []})

    params_url = f"?Nome={nome}&limit=10"
    if carrier_id:
        params_url += f"&carrier_id={carrier_id}"

    url = f"{TRANSP_API_URL}/Carriers/driver/list{params_url}"

    client = RequestClient(
        method="get",
        url=url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    )

    response_moto = client.send_api_request()

    raw_items = []
    if isinstance(response_moto, dict):
        raw_items = response_moto.get(
            "items") or response_moto.get("results") or []
    elif isinstance(response_moto, list):
        raw_items = response_moto

    items = []
    for item in raw_items:
        items.append({
            "uid": item.get("uid", ""),
            "name": item.get("name") or item.get("nome") or "",
        })

    return JsonResponse({"items": items})


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.transportes', raise_exception=True)
def lista_viagens(request):
    titulo = "Lista de Viagens"
    travels = []

    filtro_campos = [
        "travel_id",
        "cliente",
        "transportadora",
        "pa_selecionada",
        "tipo_servico",
        "driver_nome",
        "driver_id",
        "status_id",
        "sem_motorista",
        "status_list",
        "cep_origin",
        "cep_destin",
        "offset",
        "limit",
        "created_at",
        "designation_id",
        "atrasado"
    ]

    url_cliente = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_cliente,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()
    if isinstance(resp, dict) and resp.get("detail"):
        resp = []

    clientes_map = {
        str(c.get("id")): c.get("nome") or c.get("name") or str(c.get("id"))
        for c in resp
    }

    tipos_por_cliente = {}
    status_por_tipo = {}

    for cliente in resp:
        cliente_id = str(cliente.get("id"))
        order_types = cliente.get("OrderType", []) or []

        tipos_por_cliente[cliente_id] = [
            {
                "id": str(ot.get("id")),
                "type": ot.get("type", ""),
                "description": ot.get("description", "") or ot.get("type", ""),
            }
            for ot in order_types
        ]

        for ot in order_types:
            tipo_id = str(ot.get("id"))
            status_por_tipo[tipo_id] = [
                {
                    "id": str(st.get("id")),
                    "type": st.get("type", ""),
                    "description": st.get("description", "") or st.get("type", ""),
                }
                for st in (ot.get("status", []) or [])
            ]

    url_transportadora = f"{TRANSP_API_URL}/Carriers/list"
    client = RequestClient(
        method="get",
        url=url_transportadora,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp_transportadora = client.send_api_request()
    if isinstance(resp_transportadora, dict) and resp_transportadora.get("detail"):
        resp_transportadora = []

    if request.method == "POST" and "limpar_filtros" in request.POST:
        request.session["filtro_viagem"] = {}
        return redirect("transportes:lista_viagens")

    if request.method == "POST" and ("enviar_evento" in request.POST or "extrair_travels" in request.POST):
        request.session["filtro_viagem"] = {
            campo: request.POST.get(campo, "")
            for campo in filtro_campos
        }

    filtros = request.session.get("filtro_viagem", {})

    form = ListaViagensForm(
        initial={campo: filtros.get(campo, "") for campo in filtro_campos},
        nome_form=titulo,
        clientes=resp,
        transportadoras=resp_transportadora,
        user=request.user,
    )

    cliente_selecionado = str(filtros.get("cliente", "")).strip()
    tipo_servico_selecionado = str(filtros.get("tipo_servico", "")).strip()

    if "tipo_servico" in form.fields:
        tipos_choices = [("", "Selecione")]
        for item in tipos_por_cliente.get(cliente_selecionado, []):
            label = item["type"]
            if item["description"] and item["description"] != item["type"]:
                label = f'{item["type"]} - {item["description"]}'
            tipos_choices.append((item["id"], label))
        form.fields["tipo_servico"].choices = tipos_choices

    if "status_list" in form.fields:
        status_choices = [("", "Selecione")]
        for item in status_por_tipo.get(tipo_servico_selecionado, []):
            label = item["type"]
            if item["description"] and item["description"] != item["type"]:
                label = f'{item["type"]} - {item["description"]}'
            status_choices.append((item["id"], label))
        form.fields["status_list"].choices = status_choices

    tipos_map = {}
    status_map = {}
    tipo_api_map = {}
    status_api_map = {}

    for cliente in resp:
        for ot in cliente.get("OrderType", []) or []:
            tipo_id = str(ot.get("id"))
            tipo_label = ot.get("description") or ot.get("type") or tipo_id

            tipos_map[tipo_id] = tipo_label
            tipo_api_map[tipo_id] = ot.get("type", "")

            for st in ot.get("status", []) or []:
                status_id = str(st.get("id"))
                status_label = st.get("type") or st.get(
                    "description") or status_id

                status_map[status_id] = status_label
                status_api_map[status_id] = st.get("type", "")

    filtros_ativos = sum(
        1 for campo in filtro_campos
        if filtros.get(campo) not in [None, ""]
    )

    if filtros_ativos:
        try:
            params = {}

            for campo in filtro_campos:
                valor = filtros.get(campo)

                if valor in [None, "", [], ()]:
                    continue

                if campo in ["designation_id", "driver_nome", "created_at", "offset", "limit", "status_id"]:
                    continue

                if campo == "pa_selecionada":
                    params["designation_id"] = valor

                elif campo == "tipo_servico":
                    params["tipo_servico"] = tipo_api_map.get(
                        str(valor), valor)

                elif campo == "status_list":
                    params["status_list"] = status_api_map.get(
                        str(valor), valor)

                elif campo == "atrasado":
                    params["atrasado"] = str(valor).lower()

                else:
                    params[campo] = valor

            url_travel = f"{TRANSP_API_URL}/v2/order_travel/list/general?{urlencode(params)}"

            client = RequestClient(
                method="get",
                url=url_travel,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            resp_travel = client.send_api_request()

            if 'detail' in resp_travel:
                messages.error(request, resp_travel.get('detail'))
            else:
                messages.success(request, "Consulta realizada com sucesso!")

            if isinstance(resp_travel, list):
                travels = resp_travel

            for t in travels:
                travel_data = t.get("travel", {})

                travel_data["start_date_formatada"] = formatar_data(
                    travel_data.get("start_date")
                )
                travel_data["end_date_formatada"] = formatar_data(
                    travel_data.get("end_date")
                )
                travel_data["created_at_formatada"] = formatar_data(
                    travel_data.get("created_at")
                )

        except Exception:
            travels = []

    paginator = Paginator(travels, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    filtros_exibicao = []

    mapa_campos = {
        "travel_id": "Travel",
        "cliente": "Cliente",
        "transportadora": "Transportadora",
        "pa_selecionada": "PA",
        "tipo_servico": "Tipo servico",
        "driver_id": "Motorista",
        "driver_nome": "Motorista",
        "status_id": "Status",
        "sem_motorista": "Sem motorista",
        "status_list": "Lista status",
        "cep_origin": "CEP origem",
        "cep_destin": "CEP destino",
        "created_at": "Data criação",
        "designation_id": "Designation",
        "atrasado": "Atrasadas",
    }

    clientes_map = {
        str(c.get("id")): c.get("nome") or c.get("name") or str(c.get("id"))
        for c in resp
    }

    transportadoras_map = {
        str(t.get("id")): t.get("name") or t.get("nome") or str(t.get("id"))
        for t in resp_transportadora
    }

    for campo in filtro_campos:
        valor = filtros.get(campo)

        if valor in [None, "", [], ()]:
            continue

        if campo == "driver_id":
            continue

        valor_exibicao = valor

        if campo == "cliente":
            valor_exibicao = clientes_map.get(str(valor), valor)

        elif campo == "transportadora":
            valor_exibicao = transportadoras_map.get(str(valor), valor)

        elif campo == "tipo_servico":
            valor_exibicao = tipos_map.get(str(valor), valor)

        elif campo == "status_list":
            valor_exibicao = status_map.get(str(valor), valor)

        elif campo in ["sem_motorista", "atrasado"]:
            valor_exibicao = "Sim" if str(valor).lower() in [
                "true", "1", "on"] else "Não"

        elif isinstance(valor, str):
            valor_exibicao = valor.strip().capitalize()

        filtros_exibicao.append({
            "campo": mapa_campos.get(campo, campo.replace("_", " ").capitalize()),
            "valor": valor_exibicao,
        })

    if request.method == 'POST':
        if "extrair_travels" in request.POST:
            try:
                extract_params = {}

                travel_id = filtros.get("travel_id")
                if travel_id not in [None, "", [], ()]:
                    extract_params["travel_id"] = travel_id

                cliente = filtros.get("cliente")
                if cliente not in [None, "", [], ()]:
                    extract_params["cliente"] = cliente

                transportadora = filtros.get("transportadora")
                if transportadora not in [None, "", [], ()]:
                    extract_params["transportadora"] = transportadora

                pa_selecionada = filtros.get("pa_selecionada")
                if pa_selecionada not in [None, "", [], ()]:
                    extract_params["designation_id"] = pa_selecionada

                tipo_servico = filtros.get("tipo_servico")
                if tipo_servico not in [None, "", [], ()]:
                    extract_params["tipo_servico"] = tipos_map.get(
                        str(tipo_servico), tipo_servico)

                driver_id = filtros.get("driver_id")
                if driver_id not in [None, "", [], ()]:
                    extract_params["driver_id"] = driver_id

                sem_motorista = filtros.get("sem_motorista")
                if sem_motorista not in [None, "", [], ()]:
                    extract_params["sem_motorista"] = sem_motorista

                atrasado = filtros.get("atrasado")
                if atrasado not in [None, "", [], ()]:
                    extract_params["atrasado"] = str(atrasado).lower()

                status_list = filtros.get("status_list")
                if status_list not in [None, "", [], ()]:
                    extract_params["status_list"] = status_api_map.get(
                        str(status_list), status_list)

                cep_origin = filtros.get("cep_origin")
                if cep_origin not in [None, "", [], ()]:
                    extract_params["cep_origin"] = cep_origin

                cep_destin = filtros.get("cep_destin")
                if cep_destin not in [None, "", [], ()]:
                    extract_params["cep_destin"] = cep_destin

                url_extract = f"{TRANSP_API_URL}/v2/order_travel/export/general/excel?{urlencode(extract_params)}"

                return redirect(url_extract)

            except Exception as e:
                messages.error(
                    request, f"Erro ao extrair travels: {str(e)}")
                return redirect("transportes:lista_viagens")

    return render(request, 'transportes/transportes/lista_viagens.html', {
        "botao_texto": "Consultar",
        "current_parent_menu": "transportes",
        "current_menu": "lista_viagens",
        "site_title": titulo,
        "form": form,
        "travels": page_obj,
        "filtros_ativos": filtros_ativos,
        "filtros": filtros,
        "filtros_exibicao": filtros_exibicao,
        "tipos_por_cliente": tipos_por_cliente,
        "status_por_tipo": status_por_tipo,
    })
