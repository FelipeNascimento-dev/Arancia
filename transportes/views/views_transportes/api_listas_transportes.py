"""Endpoints JSON para lazy-load de modais nas listas."""

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from transportes.services.consulta_os_service import fetch_order_travels
from transportes.services.lista_viagens_service import fetch_travel_events


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
