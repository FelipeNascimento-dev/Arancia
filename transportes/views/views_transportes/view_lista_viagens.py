from urllib import request

from django.shortcuts import render, redirect

from transportes.utils import filtros
from ...forms import ListaViagensForm
from setup.local_settings import TRANSP_API_URL
from django.contrib import messages
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from datetime import datetime
from urllib.parse import urlencode
from django.http import JsonResponse
import json

from transportes.models import FiltroPadraoTela, FiltroFavoritoUsuario
from transportes.utils.filtros import (
    obter_filtros_tela,
    salvar_filtro_favorito,
    limpar_filtro_favorito,
)


def formatar_data(data_str, com_hora=True):
    if not data_str or data_str == "None":
        return None

    try:
        dt = datetime.fromisoformat(str(data_str).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")
    except Exception:
        return data_str


HARDCODE_PENDING_STATUS = {
    "id": "PENDING",
    "type": "PENDING",
    "description": "PENDING",
}


def montar_filtros_lista_viagens(post_data, filtro_campos):
    filtros = {}

    campos_multiplos = {"tipo_servico", "status_list"}

    for campo in filtro_campos:
        if campo in campos_multiplos:
            valor = post_data.getlist(campo)
            valor = [v.strip() for v in valor if str(v).strip()]
        else:
            valor = post_data.get(campo, "")
            if isinstance(valor, str):
                valor = valor.strip()

        filtros[campo] = valor

    return filtros


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
    chave_tela = FiltroFavoritoUsuario.TELA_LISTA_VIAGENS
    modal_travel_event = False
    travels = []
    selected_travel_ids = []
    travel_event_types = []
    travel_items = []

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
        "atrasado",
        "Response",
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

            statuses_raw = [
                {
                    "id": str(st.get("id")),
                    "type": st.get("type", ""),
                    "description": st.get("description", "") or st.get("type", ""),
                }
                for st in (ot.get("status", []) or [])
            ]

            pending_existe = any(
                str(item.get("type", "")).strip().upper() == "PENDING"
                or str(item.get("id", "")).strip().upper() == "PENDING"
                for item in statuses_raw
            )

            if not pending_existe:
                statuses_raw.insert(0, HARDCODE_PENDING_STATUS.copy())

            status_por_tipo[tipo_id] = statuses_raw

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

    filtros = {}

    if request.method == "POST":
        if "limpar_filtros" in request.POST:
            return redirect(f"{request.path}?limpo=1")

        filtros_post = montar_filtros_lista_viagens(
            request.POST, filtro_campos)

        if not filtros_post.get("Response"):
            filtros_post["Response"] = "resume"

        if "salvar_favorito" in request.POST:
            salvar_filtro_favorito(
                usuario=request.user,
                chave_tela=chave_tela,
                filtros=filtros_post,
            )
            messages.success(request, "Filtro favorito salvo com sucesso.")
            return redirect("transportes:lista_viagens")

        if "usar_padrao" in request.POST:
            filtro_padrao = FiltroPadraoTela.objects.filter(
                chave_tela=chave_tela,
                ativo=True
            ).first()

            if filtro_padrao and filtro_padrao.filtros:
                filtros = filtro_padrao.filtros
                filtros["Response"] = filtros.get("Response") or "resume"
                messages.success(request, "Filtro padrão aplicado.")
            else:
                filtros = {"Response": "resume"}
                messages.warning(
                    request, "Nenhum filtro padrão cadastrado para esta tela.")

        elif "enviar_evento" in request.POST or "extrair_travels" in request.POST:
            filtros = filtros_post

        else:
            filtros = obter_filtros_tela(request.user, chave_tela) or {}
            filtros["Response"] = filtros.get("Response") or "resume"

    else:
        limpou_tela = request.GET.get("limpo") == "1"

        if limpou_tela:
            filtros = {"Response": "resume"}
        else:
            filtros = obter_filtros_tela(request.user, chave_tela) or {}
            filtros["Response"] = filtros.get("Response") or "resume"

    usuario_eh_arancia_pa = request.user.groups.filter(
        name="arancia_PA").exists()

    user_designation = None
    user_designation_id = ""
    user_designation_nome = ""
    usuario_eh_arancia_pa = request.user.groups.filter(
        name="arancia_PA").exists()

    if usuario_eh_arancia_pa:
        user_designation = getattr(
            getattr(request.user, "designacao", None), "informacao_adicional", None)

        if user_designation is not None:
            user_designation_id = str(
                getattr(user_designation, "id", "") or "").strip()
            user_designation_nome = str(
                getattr(user_designation, "nome", "") or "").strip()

        pa_filtro = str(filtros.get("pa_selecionada", "") or "").strip()

        if user_designation_id:
            if pa_filtro and pa_filtro != user_designation_id:
                messages.error(
                    request,
                    "Você só pode consultar viagens da sua própria PA."
                )
                return redirect("transportes:lista_viagens")

            filtros["pa_selecionada"] = user_designation_id

    initial_data = {}
    for campo in filtro_campos:
        if campo in {"tipo_servico", "status_list"}:
            valor = filtros.get(campo, [])
            if isinstance(valor, str):
                valor = [valor] if valor else []
            initial_data[campo] = valor
        else:
            initial_data[campo] = filtros.get(campo, "")

    form = ListaViagensForm(
        initial=initial_data,
        nome_form=titulo,
        clientes=resp,
        transportadoras=resp_transportadora,
        user=request.user,
    )

    if usuario_eh_arancia_pa:
        if user_designation_id and "pa_selecionada" in form.fields:
            form.fields["pa_selecionada"].choices = [
                (user_designation_id, user_designation_nome or user_designation_id)
            ]
            form.fields["pa_selecionada"].initial = user_designation_id
            form.fields["pa_selecionada"].widget.attrs["readonly"] = True
            form.fields["pa_selecionada"].widget.attrs["onclick"] = "return false;"
            form.fields["pa_selecionada"].widget.attrs["onmousedown"] = "return false;"

    cliente_selecionado = str(filtros.get("cliente", "")).strip()

    tipos_servico_selecionados = filtros.get("tipo_servico", [])
    if isinstance(tipos_servico_selecionados, str):
        tipos_servico_selecionados = [
            tipos_servico_selecionados] if tipos_servico_selecionados else []

    if "tipo_servico" in form.fields:
        tipos_choices = []
        for item in tipos_por_cliente.get(cliente_selecionado, []):
            label = item["type"]
            if item["description"] and item["description"] != item["type"]:
                label = f'{item["type"]} - {item["description"]}'
            tipos_choices.append((item["id"], label))
        form.fields["tipo_servico"].choices = tipos_choices

    if "status_list" in form.fields:
        status_choices = []
        status_ids_adicionados = set()

        for tipo_id in tipos_servico_selecionados:
            for item in status_por_tipo.get(str(tipo_id), []):
                if item["id"] in status_ids_adicionados:
                    continue

                status_ids_adicionados.add(item["id"])

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

            statuses_do_tipo = list(ot.get("status", []) or [])

            pending_existe = any(
                str(st.get("type", "")).strip().upper() == "PENDING"
                or str(st.get("id", "")).strip().upper() == "PENDING"
                for st in statuses_do_tipo
            )

            if not pending_existe:
                statuses_do_tipo.insert(0, HARDCODE_PENDING_STATUS.copy())

            for st in statuses_do_tipo:
                status_id = str(st.get("id"))
                status_label = st.get("type") or st.get(
                    "description") or status_id

                status_map[status_id] = status_label
                status_api_map[status_id] = st.get("type", "") or status_id

    filtros_ativos = sum(
        1 for campo in filtro_campos
        if campo != "Response" and filtros.get(campo) not in [None, ""]
    )

    response_mode = filtros.get("Response") or "resume"

    if filtros_ativos or response_mode:
        try:
            params = {}

            for campo in filtro_campos:
                valor = filtros.get(campo)

                if campo == "Response":
                    params["Response"] = valor or "resume"
                    continue

                if valor in [None, "", [], ()]:
                    continue

                if campo in ["designation_id", "driver_nome", "created_at", "offset", "limit", "status_id"]:
                    continue

                if campo == "pa_selecionada":
                    params["designation_id"] = valor

                elif campo == "tipo_servico":
                    tipos_api = []
                    for item in valor:
                        mapped = tipo_api_map.get(str(item), item)
                        if mapped and mapped not in tipos_api:
                            tipos_api.append(mapped)

                    if tipos_api:
                        params["order_type"] = ",".join(tipos_api)

                elif campo == "status_list":
                    status_api = []
                    for item in valor:
                        mapped = status_api_map.get(str(item), item)
                        if mapped and mapped not in status_api:
                            status_api.append(mapped)

                    if status_api:
                        params["status"] = ",".join(status_api)

                elif campo == "atrasado":
                    params["atrasado"] = str(valor).lower()

                else:
                    params[campo] = valor

            if "Response" not in params:
                params["Response"] = "resume"

            url_travel = f"{TRANSP_API_URL}/v2/order_travel/list/general?{urlencode(params, safe=',')}"

            client = RequestClient(
                method="get",
                url=url_travel,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            resp_travel = client.send_api_request()

            if isinstance(resp_travel, dict) and resp_travel.get("detail"):
                messages.error(request, resp_travel.get("detail"))
            else:
                if request.method == "POST" and "enviar_evento" in request.POST:
                    messages.success(
                        request, "Consulta realizada com sucesso!")

            if isinstance(resp_travel, list):
                travels = resp_travel

            for t in travels:
                travel_data = t.get("travel", {})
                travel_data["start_date_formatada"] = formatar_data(
                    travel_data.get("start_date"))
                travel_data["end_date_formatada"] = formatar_data(
                    travel_data.get("end_date"))
                travel_data["created_at_formatada"] = formatar_data(
                    travel_data.get("created_at"))

                eventos = t.get("travel_events", []) or []

                for ev in eventos:
                    ev["created_at_formatada"] = formatar_data(
                        ev.get("created_at"))
                    evento_info = ev.get("evento", {}) or {}

                    ev["evento_nome"] = evento_info.get("name", "")
                    ev["evento_descricao"] = evento_info.get("description", "")
                    ev["evento_tipo"] = evento_info.get("type", "")

                eventos.sort(key=lambda x: x.get("created_at") or "")

                t["travel_events"] = eventos
                t["travel_events_count"] = len(eventos)
                t["travel_events_json"] = json.dumps(
                    eventos, ensure_ascii=False, default=str)

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
        "Response": "Response",
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
            if isinstance(valor, list):
                valor_exibicao = ", ".join(
                    tipos_map.get(str(v), str(v)) for v in valor
                )
            else:
                valor_exibicao = tipos_map.get(str(valor), valor)

        elif campo == "status_list":
            if isinstance(valor, list):
                valor_exibicao = ", ".join(
                    status_map.get(str(v), str(v)) for v in valor
                )
            else:
                valor_exibicao = status_map.get(str(valor), valor)
        elif campo in ["sem_motorista", "atrasado"]:
            valor_exibicao = "Sim" if str(valor).lower() in [
                "true", "1", "on"] else "Não"
        elif campo == "Response":
            valor_exibicao = "Detalhado" if str(
                valor).lower() == "detailed" else "Resumido"
        elif isinstance(valor, str):
            valor_exibicao = valor.strip().capitalize()

        filtros_exibicao.append({
            "campo": mapa_campos.get(campo, campo.replace("_", " ").capitalize()),
            "valor": valor_exibicao,
        })

    if request.method == "POST" and "extrair_travels" in request.POST:
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
                tipos_api = []
                for item in tipo_servico:
                    mapped = tipo_api_map.get(str(item), item)
                    if mapped and mapped not in tipos_api:
                        tipos_api.append(mapped)

                if tipos_api:
                    extract_params["tipo_servico"] = ",".join(tipos_api)

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
                status_api = []
                for item in status_list:
                    mapped = status_api_map.get(str(item), item)
                    if mapped and mapped not in status_api:
                        status_api.append(mapped)

                if status_api:
                    extract_params["status_list"] = ",".join(status_api)

            cep_origin = filtros.get("cep_origin")
            if cep_origin not in [None, "", [], ()]:
                extract_params["cep_origin"] = cep_origin

            cep_destin = filtros.get("cep_destin")
            if cep_destin not in [None, "", [], ()]:
                extract_params["cep_destin"] = cep_destin

            extract_params["Response"] = filtros.get("Response") or "resume"

            url_extract = f"{TRANSP_API_URL}/v2/order_travel/export/general/excel?{urlencode(extract_params)}"
            return redirect(url_extract)

        except Exception as e:
            messages.error(request, f"Erro ao extrair travels: {str(e)}")
            return redirect("transportes:lista_viagens")

    if request.method == "POST" and "criar_eventos_cards" in request.POST:
        selected_travel_ids = request.POST.getlist("travels_selecionadas")
        modal_travel_event = True

        if selected_travel_ids:
            try:
                client_id = (request.POST.get("cliente")
                             or filtros.get("cliente") or "").strip()
                tipo_servico_id = (request.POST.get(
                    "tipo_servico") or filtros.get("tipo_servico") or "").strip()

                cliente_nome = ""
                if client_id:
                    for c in resp:
                        if str(c.get("id")) == str(client_id):
                            cliente_nome = c.get("nome") or c.get("name") or ""
                            break

                order_type_api = ""
                if tipo_servico_id:
                    order_type_api = tipo_api_map.get(tipo_servico_id, "")

                if cliente_nome and order_type_api:
                    query = urlencode({
                        "status": "true",
                        "cliente": cliente_nome,
                        "order_type": tipo_servico_id,
                    })

                    url = f"{TRANSP_API_URL}/order_events_types/list?{query}"

                    client = RequestClient(
                        method="GET",
                        url=url,
                        headers={
                            "accept": "application/json",
                            "Content-Type": "application/json",
                        },
                    )

                    response_travel = client.send_api_request()

                    if isinstance(response_travel, list):
                        travel_event_types = [
                            ev for ev in response_travel
                            if str(ev.get("active")).lower() == "true"
                        ]

                        if not travel_event_types:
                            messages.warning(
                                request,
                                f"Nenhum tipo de evento encontrado para cliente '{cliente_nome}' e tipo '{order_type_api}'."
                            )

                    elif isinstance(response_travel, dict) and response_travel.get("detail"):
                        messages.error(request, response_travel.get("detail"))

                    else:
                        messages.warning(
                            request, "A API não retornou eventos em formato esperado.")
                else:
                    messages.warning(
                        request,
                        f"Selecione cliente e tipo de serviço válidos. Cliente='{client_id}' | Tipo='{tipo_servico_id}'"
                    )

            except Exception as e:
                messages.error(request, f"Erro ao consultar eventos: {e}")

    if request.method == "POST" and "atrelar_motorista_lote" in request.POST:
        selected_travel_ids = request.POST.getlist("travels_selecionadas")
        motorista_id = (request.POST.get("motorista_id") or "").strip()
        motorista_nome = (request.POST.get("motorista_nome") or "").strip()
        created_by = request.user.username

        if not selected_travel_ids:
            messages.error(request, "Selecione pelo menos uma viagem.")
            return redirect("transportes:lista_viagens")

        if not motorista_id:
            messages.error(request, "Selecione um motorista válido.")
            return redirect("transportes:lista_viagens")

        try:
            ids_limpos = [
                int(str(travel_id).strip())
                for travel_id in selected_travel_ids
                if str(travel_id).strip()
            ]

            payload_update = [
                {
                    "travels_ids": ids_limpos,
                    "driver_id": int(motorista_id),
                }
            ]

            url_update = (
                f"{TRANSP_API_URL}/v2/order_travel/driver/updated?created_by={created_by}"
            )

            client = RequestClient(
                method="POST",
                url=url_update,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                request_data=payload_update,
            )

            response_update = client.send_api_request()

            if isinstance(response_update, dict) and response_update.get("detail"):
                detail = response_update.get("detail")
                if isinstance(detail, list):
                    detail = " | ".join(str(item) for item in detail)
                messages.error(request, f"Erro ao atrelar motorista: {detail}")
            else:
                messages.success(
                    request,
                    f"Motorista {motorista_nome or motorista_id} vinculado com sucesso às viagens selecionadas."
                )

            return redirect("transportes:lista_viagens")

        except Exception as e:
            messages.error(request, f"Erro ao atrelar motorista: {e}")
            return redirect("transportes:lista_viagens")

    if request.method == "POST" and "criar_evento_travel_lote" in request.POST:
        selected_travel_ids = request.POST.getlist("travels_selecionadas")

        try:
            event_type_id = int(request.POST.get("event_type_id"))
        except:
            messages.error(request, "Selecione um tipo de evento.")
            return redirect("transportes:lista_viagens")

        description = (request.POST.get("description") or "").strip()
        created_by = request.user.username
        location_lat = (request.POST.get("location_lat") or "").strip()
        location_long = (request.POST.get("location_long") or "").strip()

        payload_event = {
            "event_type_id": event_type_id,
            "created_by": created_by,
        }

        if description:
            payload_event["description"] = description
        if location_lat:
            payload_event["location_lat"] = location_lat
        if location_long:
            payload_event["location_long"] = location_long

        try:
            headers_api = {
                "accept": "application/json",
                "Content-Type": "application/json",
            }

            ids_limpos = [str(i)
                          for i in selected_travel_ids if str(i).strip()]
            query_ids = "&".join([f"ids={i}" for i in ids_limpos])

            url = f"{TRANSP_API_URL}/v2/order_tracking/create?destination=travel&{query_ids}"

            client = RequestClient(
                method="POST",
                url=url,
                headers=headers_api,
                request_data=payload_event
            )

            response_event = client.send_api_request()

            if isinstance(response_event, dict) and "detail" in response_event:
                messages.error(request, response_event["detail"])
            else:
                messages.success(request, "Eventos criados com sucesso!")
                return redirect("transportes:lista_viagens")

        except Exception as e:
            messages.error(request, f"Erro ao criar evento: {e}")

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
        "modal_travel_event": modal_travel_event,
        "selected_travel_ids": selected_travel_ids,
        "travel_event_types": travel_event_types,
        "travel_items": travel_items,
        "response_mode": response_mode,
    })
