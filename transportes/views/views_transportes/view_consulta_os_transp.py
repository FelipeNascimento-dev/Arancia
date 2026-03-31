from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
import math
from django.db.models import Q
from logistica.models import GroupAditionalInformation, Group
from ...forms import ConsultaOStranspForm
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from datetime import datetime
from urllib.parse import urlencode
from django.http import JsonResponse

from transportes.models import FiltroFavoritoUsuario, FiltroPadraoTela
from transportes.utils.filtros import (
    obter_filtros_tela,
    salvar_filtro_favorito,
    limpar_filtro_favorito,
)


def buscar_locais(request):
    termo = request.GET.get("q", "").strip()

    if len(termo) < 2:
        return JsonResponse({"items": []})

    grupos_base = Group.objects.filter(
        Q(name="arancia_PA") |
        Q(name="arancia_CD") |
        Q(name="arancia_CUSTOMER")
    )

    locais = (
        GroupAditionalInformation.objects
        .filter(group__in=grupos_base, nome__icontains=termo)
        .select_related("group")
        .order_by("nome")[:10]
    )

    data = []

    for l in locais:
        prefix = ""

        if l.group.name == "arancia_PA":
            prefix = "[PA]"
        elif l.group.name == "arancia_CD":
            prefix = "[CD]"
        elif l.group.name == "arancia_CUSTOMER":
            prefix = "[CUSTOMER]"

        data.append({
            "id": l.id,
            "label": f"{prefix} {l.nome}"
        })

    return JsonResponse({"items": data})


def aplicar_filtro_data(data_source, params):
    created_at = (data_source.get("created_at") or "").strip()
    data_inicial = (data_source.get("data_inicial") or "").strip()
    data_final = (data_source.get("data_final") or "").strip()

    if data_inicial and data_final:
        params["data_inicial"] = data_inicial
        params["data_final"] = data_final
    elif data_inicial:
        params["created_at"] = data_inicial
    elif data_final:
        params["created_at"] = data_final
    elif created_at:
        params["created_at"] = created_at


def montar_filtros_consulta_os(post_data):
    return {
        "numero_os": (post_data.get("numero_os") or "").strip(),
        "tipo_os": (post_data.get("tipo_os") or "").strip(),
        "client": (post_data.get("client") or "").strip(),
        "pa_selecionada": (post_data.get("pa_selecionada") or "").strip(),
        "origem": (post_data.get("origem") or "").strip(),
        "destino": (post_data.get("destino") or "").strip(),
        "data_inicial": (post_data.get("data_inicial") or "").strip(),
        "data_final": (post_data.get("data_final") or "").strip(),
        "created_at": (post_data.get("created_at") or "").strip(),
        "status": [v.strip() for v in post_data.getlist("status") if v.strip()],
        "order_type": [v.strip() for v in post_data.getlist("order_type") if v.strip()],
        "enviar_evento": "1",
    }


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.transportes', raise_exception=True)
def consulta_os_transp(request):
    titulo = "Consulta OS"
    chave_tela = FiltroFavoritoUsuario.TELA_CONSULTA_OS
    resultado_api = []

    url_status = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_status,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()

    if isinstance(resp, list):
        for item in resp:
            status_base = item.get("status_base")

            for order_type in item.get("OrderType", []):
                statuses = order_type.get("status", []) or []

                if status_base:
                    status_base_type = (status_base.get(
                        "type") or "").strip().lower()
                    ja_existe = any(
                        (s.get("type") or "").strip().lower() == status_base_type
                        for s in statuses
                    )
                    if status_base_type and not ja_existe:
                        statuses.append(status_base)

                status_filtrados = []
                vistos = set()

                for st in statuses:
                    stype = (st.get("type") or "").strip()
                    if not stype:
                        continue

                    chave = stype.lower()
                    if chave in vistos:
                        continue

                    vistos.add(chave)
                    status_filtrados.append(st)

                order_type["status"] = status_filtrados

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp["detail"])
        resp = []

    # ----------------------------
    # TRATAMENTO DOS FILTROS
    # ----------------------------
    if request.method == "POST":
        filtros_post = montar_filtros_consulta_os(request.POST)

        if "limpar_filtros" in request.POST:
            return redirect(request.path)

        if "remover_favorito" in request.POST:
            limpar_filtro_favorito(request.user, chave_tela)
            messages.success(request, "Filtro favorito removido com sucesso.")
            return redirect(request.path)

        if "salvar_favorito" in request.POST:
            salvar_filtro_favorito(
                usuario=request.user,
                chave_tela=chave_tela,
                filtros=filtros_post,
            )
            messages.success(request, "Filtro favorito salvo com sucesso.")
            return redirect(f"{request.path}?{urlencode(filtros_post, doseq=True)}")

        if "usar_padrao" in request.POST:
            filtro_padrao = FiltroPadraoTela.objects.filter(
                chave_tela=chave_tela,
                ativo=True
            ).first()

            if filtro_padrao and filtro_padrao.filtros:
                messages.success(request, "Filtro padrão aplicado.")
                return redirect(f"{request.path}?{urlencode(filtro_padrao.filtros, doseq=True)}")

            messages.warning(
                request, "Nenhum filtro padrão cadastrado para esta tela.")
            return redirect(request.path)

        if "extrair_os" in request.POST:
            data = request.POST.copy()
            data.pop("csrfmiddlewaretoken", None)

            extract_params = {}

            aplicar_filtro_data(data, extract_params)

            tipo_os = (data.get("tipo_os") or "").strip().upper()
            numero_os = (data.get("numero_os") or "").strip()

            if numero_os and not tipo_os:
                messages.error(
                    request, "Selecione o tipo da OS (IN/EX) para pesquisar pelo número.")
                return redirect(f"{request.path}?{urlencode(filtros_post, doseq=True)}")

            elif tipo_os and not numero_os:
                messages.error(
                    request, "Informe o número da OS para pesquisar.")
                return redirect(f"{request.path}?{urlencode(filtros_post, doseq=True)}")

            if numero_os:
                if tipo_os == "IN":
                    extract_params["IN"] = numero_os
                elif tipo_os == "EX":
                    extract_params["EX"] = numero_os

            cliente_id = (data.get("client") or "").strip()
            if cliente_id:
                cliente_obj = next((c for c in resp if str(
                    c.get("id")) == str(cliente_id)), None)
                if cliente_obj and cliente_obj.get("nome"):
                    extract_params["cliente"] = cliente_obj["nome"]

            pa_id = (data.get("pa_selecionada") or "").strip()
            if pa_id:
                extract_params["designation_id"] = pa_id

            origem_id = (data.get("origem") or "").strip()
            if origem_id:
                extract_params["origin_id"] = origem_id

            destino_id = (data.get("destino") or "").strip()
            if destino_id:
                extract_params["destin_id"] = destino_id

            status_ids = [s.strip()
                          for s in data.getlist("status") if s.strip()]
            if status_ids:
                status_textos = []
                for cliente in resp:
                    for order_type_item in cliente.get("OrderType", []):
                        for status_item in order_type_item.get("status", []):
                            if str(status_item.get("id")) in status_ids:
                                valor = status_item.get("type")
                                if valor and valor not in status_textos:
                                    status_textos.append(valor)

                if status_textos:
                    extract_params["status"] = ",".join(status_textos)

            order_type_ids = [ot.strip()
                              for ot in data.getlist("order_type") if ot.strip()]
            if order_type_ids:
                extract_params["order_type"] = ",".join(order_type_ids)

            url_extract = f"{TRANSP_API_URL}/service_orders/export/excel?{urlencode(extract_params)}"
            return redirect(url_extract)

        # consultar / submit normal
        return redirect(f"{request.path}?{urlencode(filtros_post, doseq=True)}")

    # ----------------------------
    # GET: carrega favorito/padrão
    # ----------------------------
    data = request.GET.copy()

    if not data:
        filtros_iniciais = obter_filtros_tela(request.user, chave_tela)
        if filtros_iniciais:
            return redirect(f"{request.path}?{urlencode(filtros_iniciais, doseq=True)}")

    form = ConsultaOStranspForm(data or None, payload=resp)

    try:
        page = int(data.get("page", 1))
    except ValueError:
        page = 1
    page = max(page, 1)

    limit = 20
    offset = (page - 1) * limit

    qs = data.copy()
    qs.pop("page", None)
    base_qs = qs.urlencode()

    should_query = data.get("enviar_evento") == "1"

    total = 0
    total_pages = 1
    pages = [page]
    has_prev = page > 1
    has_next = False

    filtros_exibicao = []

    if should_query:
        params = {}

        aplicar_filtro_data(data, params)

        tipo_os = (data.get("tipo_os") or "").strip().upper()
        numero_os = (data.get("numero_os") or "").strip()

        if numero_os and not tipo_os:
            messages.error(
                request, "Selecione o tipo da OS (IN/EX) para pesquisar pelo número.")
            numero_os = ""
        elif tipo_os and not numero_os:
            messages.error(request, "Informe o número da OS para pesquisar.")
            tipo_os = ""

        if numero_os:
            if tipo_os == "IN":
                params["IN"] = numero_os
            elif tipo_os == "EX":
                params["EX"] = numero_os
            else:
                messages.error(request, "Tipo de OS inválido. Use IN ou EX.")
                params.pop("IN", None)
                params.pop("EX", None)

        cliente_id = (data.get("client") or "").strip()
        if cliente_id:
            cliente_obj = next((c for c in resp if str(
                c.get("id")) == str(cliente_id)), None)
            if cliente_obj and cliente_obj.get("nome"):
                params["cliente"] = cliente_obj["nome"]
                filtros_exibicao.append(
                    {"campo": "Cliente", "valor": cliente_obj["nome"]})

        pa_id = (data.get("pa_selecionada") or "").strip()
        if pa_id:
            params["designation_id"] = pa_id
            filtros_exibicao.append({"campo": "PA", "valor": pa_id})

        origem_id = (data.get("origem") or "").strip()
        if origem_id:
            params["origin_id"] = origem_id
            filtros_exibicao.append({"campo": "Origem", "valor": origem_id})

        destino_id = (data.get("destino") or "").strip()
        if destino_id:
            params["destin_id"] = destino_id
            filtros_exibicao.append({"campo": "Destino", "valor": destino_id})

        status_ids = [s.strip() for s in data.getlist("status") if s.strip()]
        if status_ids:
            status_textos = []

            for cliente in resp:
                for order_type_item in cliente.get("OrderType", []):
                    for status_item in order_type_item.get("status", []):
                        if str(status_item.get("id")) in status_ids:
                            valor = status_item.get("type")
                            if valor and valor not in status_textos:
                                status_textos.append(valor)

            if status_textos:
                params["status"] = ",".join(status_textos)
                for st in status_textos:
                    filtros_exibicao.append({"campo": "Status", "valor": st})

        order_type_ids = [ot.strip()
                          for ot in data.getlist("order_type") if ot.strip()]
        if order_type_ids:
            params["order_type"] = ",".join(order_type_ids)

            for cliente in resp:
                for order_type_item in cliente.get("OrderType", []):
                    if str(order_type_item.get("id")) in order_type_ids:
                        filtros_exibicao.append({
                            "campo": "Tipo de OS",
                            "valor": order_type_item.get("type") or str(order_type_item.get("id"))
                        })

        if numero_os:
            filtros_exibicao.append({"campo": "Número OS", "valor": numero_os})
        if tipo_os:
            filtros_exibicao.append({"campo": "Tipo", "valor": tipo_os})
        if data.get("data_inicial"):
            filtros_exibicao.append(
                {"campo": "Data inicial", "valor": data.get("data_inicial")})
        if data.get("data_final"):
            filtros_exibicao.append(
                {"campo": "Data final", "valor": data.get("data_final")})

        params["limit"] = limit
        params["offset"] = offset

        url_lista = f"{TRANSP_API_URL}/service_orders/list"
        lista_request = RequestClient(
            method="get",
            url=url_lista,
            headers={"accept": "application/json"},
            request_data=params,
        )
        resultado_api = lista_request.send_api_request()

        if isinstance(resultado_api, dict) and resultado_api.get("detail"):
            messages.error(request, resultado_api["detail"])
            resultado_api = []
        else:
            if isinstance(resultado_api, dict):
                items = (
                    resultado_api.get("items")
                    or resultado_api.get("results")
                    or resultado_api.get("data")
                    or []
                )
                total = (
                    resultado_api.get("total")
                    or resultado_api.get("count")
                    or resultado_api.get("total_count")
                    or 0
                )
                resultado_api = items if isinstance(items, list) else []

            elif isinstance(resultado_api, list):
                total = 0
            else:
                resultado_api = []
                total = 0

            if total:
                total_pages = max(1, math.ceil(total / limit))
                has_next = page < total_pages
            else:
                has_next = len(resultado_api) == limit
                total_pages = page + (1 if has_next else 0)

            start = max(1, page - 2)
            end = min(total_pages, page + 2)
            pages = list(range(start, end + 1))

    for item in resultado_api:
        created = item.get("created_at")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                item["created_at_fmt"] = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                item["created_at_fmt"] = created

    filtros_ativos = len(filtros_exibicao)

    form.errors.pop("origem", None)
    form.errors.pop("destino", None)

    return render(
        request,
        "transportes/transportes/consulta_os_transp.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "lista_os",
            "orders": resultado_api if isinstance(resultado_api, list) else [],
            "filtros_exibicao": filtros_exibicao,
            "filtros_ativos": filtros_ativos,
            "tipos_por_cliente": {
                str(c.get("id")): [
                    {"id": str(ot.get("id")), "type": ot.get("type", "")}
                    for ot in c.get("OrderType", []) or []
                ]
                for c in resp
            },
            "status_por_tipo": {
                str(ot.get("id")): [
                    {"id": str(st.get("id")), "type": st.get("type", "")}
                    for st in (ot.get("status", []) or [])
                ]
                for c in resp
                for ot in c.get("OrderType", []) or []
            },
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": has_next,
                "prev_page": page - 1,
                "next_page": page + 1,
                "pages": pages,
                "base_qs": base_qs,
            },
        },
    )
