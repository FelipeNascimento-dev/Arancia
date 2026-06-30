from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.urls import reverse

from setup.local_settings import TRANSP_API_URL
from transportes.forms import ConsultaOStranspForm
from transportes.instrumentation import TranspApiCallTimer
from transportes.models import FiltroFavoritoUsuario, FiltroPadraoTela
from transportes.services.consulta_os_service import (
    append_view_mode_to_qs,
    build_export_params,
    build_list_params,
    build_pagination_state,
    montar_filtros_consulta_os,
)
from transportes.services.transportes_metadata_service import (
    build_status_and_order_type_maps,
    build_status_por_tipo_os,
    build_tipos_por_cliente_os,
    enrich_clientes_status,
    fetch_metadata,
)
from transportes.utils.baseline import _payload_metrics
from transportes.utils.filtros import (
    limpar_filtro_favorito,
    obter_filtros_tela,
    salvar_filtro_favorito,
)
from transportes.utils.metadata_api import get_clientes_status

# Re-export para compatibilidade com urls/__init__
__all__ = ["buscar_locais", "consulta_os_transp"]

from transportes.views.views_transportes.view_consulta_os_transp_legacy import (  # noqa: E402
    buscar_locais,
)


def _resolve_view_mode(request):
    mode = (request.GET.get("view_mode") or "cards").strip().lower()
    return "table" if mode == "table" else "cards"


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def consulta_os_transp(request):
    titulo = "Consulta OS"
    chave_tela = FiltroFavoritoUsuario.TELA_CONSULTA_OS
    view_mode = _resolve_view_mode(request)

    with TranspApiCallTimer(
        request,
        phase="clientes_status",
        url="gai/clientes/status",
    ) as status_timer:
        resp = enrich_clientes_status(get_clientes_status())
        status_timer.payload_size, _ = _payload_metrics(resp)

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp["detail"])
        resp = []

    status_by_id, order_type_by_id = build_status_and_order_type_maps(
        resp if isinstance(resp, list) else []
    )

    if request.method == "POST":
        filtros_post = montar_filtros_consulta_os(request.POST)

        if "limpar_filtros" in request.POST:
            return redirect(f"{request.path}?limpo=1")

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
                chave_tela=chave_tela, ativo=True
            ).first()
            if filtro_padrao and filtro_padrao.filtros:
                messages.success(request, "Filtro padrão aplicado.")
                return redirect(
                    f"{request.path}?{urlencode(filtro_padrao.filtros, doseq=True)}"
                )
            messages.warning(
                request, "Nenhum filtro padrão cadastrado para esta tela."
            )
            return redirect(request.path)

        if "extrair_os" in request.POST:
            data = request.POST.copy()
            data.pop("csrfmiddlewaretoken", None)
            tipo_os = (data.get("tipo_os") or "").strip().upper()
            numero_os = (data.get("numero_os") or "").strip()
            if numero_os and not tipo_os:
                messages.error(
                    request,
                    "Selecione o tipo da OS (IN/EX) para pesquisar pelo número.",
                )
                return redirect(
                    f"{request.path}?{urlencode(filtros_post, doseq=True)}"
                )
            if tipo_os and not numero_os:
                messages.error(request, "Informe o número da OS para pesquisar.")
                return redirect(
                    f"{request.path}?{urlencode(filtros_post, doseq=True)}"
                )
            extract_params = build_export_params(
                data, status_by_id, resp if isinstance(resp, list) else []
            )
            url_extract = (
                f"{TRANSP_API_URL}/service_orders/export/excel?"
                f"{urlencode(extract_params)}"
            )
            return redirect(url_extract)

        return redirect(f"{request.path}?{urlencode(filtros_post, doseq=True)}")

    data = request.GET.copy()
    limpou_tela = data.get("limpo") == "1"
    if limpou_tela:
        data = data.copy()
        data.pop("limpo", None)
    elif not data:
        filtros_iniciais = obter_filtros_tela(request.user, chave_tela)
        if filtros_iniciais:
            return redirect(
                f"{request.path}?{urlencode(filtros_iniciais, doseq=True)}"
            )

    form = ConsultaOStranspForm(data or None, payload=resp)

    try:
        page = int(data.get("page", 1))
    except ValueError:
        page = 1
    page = max(page, 1)

    qs = data.copy()
    qs.pop("page", None)
    base_qs_no_view = qs.urlencode()
    base_qs = append_view_mode_to_qs(base_qs_no_view, view_mode)

    should_query = data.get("enviar_evento") == "1"
    resultado_api = []
    total = 0
    filtros_exibicao = []
    async_list_load = False
    consultando = False
    pagination = build_pagination_state(page, total, len(resultado_api))
    pagination["base_qs"] = base_qs

    if should_query:
        _, filtros_exibicao, errors = build_list_params(
            data, status_by_id, order_type_by_id, resp if isinstance(resp, list) else []
        )
        for err in errors:
            messages.error(request, err)

        if not errors:
            consultando = True
            async_list_load = True

    filtros_ativos = len(filtros_exibicao)
    form.errors.pop("origem", None)
    form.errors.pop("destino", None)

    clientes_list = resp if isinstance(resp, list) else []

    return render(
        request,
        "transportes/transportes/consulta_os_transp.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "lista_os",
            "orders": resultado_api,
            "filtros_exibicao": filtros_exibicao,
            "filtros_ativos": filtros_ativos,
            "tipos_por_cliente": build_tipos_por_cliente_os(clientes_list),
            "status_por_tipo": build_status_por_tipo_os(clientes_list),
            "pagination": pagination,
            "view_mode": view_mode,
            "consultando": consultando,
            "async_list_load": async_list_load,
            "base_qs_no_view": base_qs_no_view,
            "consulta_os_js_config": {
                "filtros_ativos": filtros_ativos,
                "async_list_load": async_list_load,
                "urls": {
                    "order_travels": reverse("transportes:api_order_travels"),
                    "list_results": reverse("transportes:api_consulta_os_list"),
                },
            },
        },
    )
