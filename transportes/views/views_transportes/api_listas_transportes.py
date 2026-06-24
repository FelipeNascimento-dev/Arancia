"""Endpoints JSON para lazy-load de modais e listagens assíncronas."""

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.template.loader import render_to_string

from transportes.instrumentation import TranspApiCallTimer
from transportes.services.consulta_os_service import (
    load_orders_page,
    fetch_order_travels,
)
from transportes.services.lista_viagens_service import (
    SESSION_KEY_LISTA_VIAGENS_FILTROS,
    fetch_travel_events,
    load_travels_page,
)
from transportes.services.transportes_metadata_service import (
    FILTRO_CAMPOS_LISTA_VIAGENS,
    build_clientes_transportadoras_maps,
    build_status_and_order_type_maps,
    build_tipos_status_maps,
    enrich_clientes_status,
    fetch_metadata,
)
from transportes.utils.baseline import _payload_metrics
from transportes.utils.filtros import obter_filtros_tela
from transportes.utils.metadata_api import get_clientes_status
from transportes.models import FiltroFavoritoUsuario


def _resolve_view_mode(request):
    mode = (request.GET.get("view_mode") or "cards").strip().lower()
    return "table" if mode == "table" else "cards"


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def api_travel_events(request, travel_id):
    try:
        travel_id = int(travel_id)
    except (TypeError, ValueError):
        return JsonResponse({"detail": "ID de viagem inválido."}, status=400)

    eventos, detail = fetch_travel_events(travel_id)
    if detail:
        return JsonResponse({"detail": detail}, status=502)
    return JsonResponse({"events": eventos, "travel_id": travel_id})


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def api_order_travels(request):
    order_number = (request.GET.get("order_number") or "").strip()
    if not order_number:
        return JsonResponse({"detail": "Informe order_number."}, status=400)

    travels, detail = fetch_order_travels(order_number)
    if detail:
        return JsonResponse({"detail": detail}, status=502)
    return JsonResponse({"travels": travels, "order_number": order_number})


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def api_consulta_os_list(request):
    if request.GET.get("enviar_evento") != "1":
        return JsonResponse({"detail": "Consulta não solicitada."}, status=400)

    view_mode = _resolve_view_mode(request)
    data = request.GET.copy()

    with TranspApiCallTimer(
        request,
        phase="service_order_list",
        url="v2/service_order/list",
    ) as list_timer:
        resp = enrich_clientes_status(get_clientes_status())
        clientes_list = resp if isinstance(resp, list) else []
        status_by_id, order_type_by_id = build_status_and_order_type_maps(
            clientes_list
        )

        page_result = load_orders_page(
            data,
            data.get("page", 1),
            status_by_id,
            order_type_by_id,
            clientes_list,
            view_mode=view_mode,
        )
        list_timer.payload_size = 0

    errors = page_result.get("errors") or []
    if errors:
        return JsonResponse({"detail": errors[0], "errors": errors}, status=400)

    html = render_to_string(
        "transportes/transportes/partials/_consulta_os_results.html",
        {
            "orders": page_result["orders"],
            "pagination": page_result["pagination"],
            "view_mode": view_mode,
        },
        request=request,
    )
    return JsonResponse({
        "html": html,
        "total": page_result["total"],
    })


def _resolve_lista_viagens_filtros(request):
    chave_tela = FiltroFavoritoUsuario.TELA_LISTA_VIAGENS
    limpou_tela = request.GET.get("limpo") == "1"
    if limpou_tela:
        return {"Response": "resume"}

    if (
        "page" in request.GET
        and SESSION_KEY_LISTA_VIAGENS_FILTROS in request.session
    ):
        filtros = dict(request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS])
    else:
        filtros = obter_filtros_tela(request.user, chave_tela) or {}

    filtros["Response"] = filtros.get("Response") or "resume"
    return filtros


def _enforce_pa_scope_lista_viagens(request, filtros):
    usuario_eh_arancia_pa = request.user.groups.filter(name="arancia_PA").exists()
    if not usuario_eh_arancia_pa:
        return filtros, None

    user_designation = getattr(
        getattr(request.user, "designacao", None),
        "informacao_adicional",
        None,
    )
    user_designation_id = str(getattr(user_designation, "id", "") or "").strip()
    if not user_designation_id:
        return filtros, None

    pa_filtro = str(filtros.get("pa_selecionada", "") or "").strip()
    if pa_filtro and pa_filtro != user_designation_id:
        return filtros, "Você só pode consultar viagens da sua própria PA."

    filtros["pa_selecionada"] = user_designation_id
    return filtros, None


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def api_lista_viagens_list(request):
    filtros = _resolve_lista_viagens_filtros(request)
    filtros, pa_error = _enforce_pa_scope_lista_viagens(request, filtros)
    if pa_error:
        return JsonResponse({"detail": pa_error}, status=403)

    filtros_ativos = sum(
        1
        for campo in FILTRO_CAMPOS_LISTA_VIAGENS
        if campo != "Response" and filtros.get(campo) not in [None, ""]
    )
    response_mode = filtros.get("Response") or "resume"
    if not filtros_ativos and not response_mode:
        return JsonResponse({"detail": "Nenhum filtro para consulta."}, status=400)

    view_mode = _resolve_view_mode(request)

    with TranspApiCallTimer(
        request,
        phase="order_travel_list",
        url="order_travel/list",
    ) as travel_timer:
        metadata = fetch_metadata()
        resp = metadata["clientes_status"]
        resp_transportadora = metadata["carriers_list"]
        size_clientes, _ = _payload_metrics(resp)
        size_carriers, _ = _payload_metrics(resp_transportadora)
        travel_timer.payload_size = size_clientes + size_carriers

        maps_ctx = build_tipos_status_maps(resp)
        clientes_map, transportadoras_map = build_clientes_transportadoras_maps(
            resp, resp_transportadora
        )
        maps_ctx["clientes_transportadoras_maps"] = (
            clientes_map,
            transportadoras_map,
        )

        page_result = load_travels_page(
            filtros,
            request.GET.get("page", 1),
            maps_ctx,
            request,
            response_mode=response_mode,
            view_mode=view_mode,
        )

    errors = page_result.get("errors") or []
    if errors:
        return JsonResponse({"detail": errors[0], "errors": errors}, status=502)

    request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS] = filtros

    html = render_to_string(
        "transportes/transportes/partials/_lista_viagens_results.html",
        {
            "travels": page_result["travels"],
            "pagination": page_result["pagination"],
            "view_mode": view_mode,
            "filtros": page_result["filtros"],
            "response_mode": page_result["response_mode"],
            "show_origin_column": page_result["show_origin_column"],
        },
        request=request,
    )
    return JsonResponse({
        "html": html,
        "total": page_result["total"],
    })
