from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.urls import reverse

from transportes.forms import ListaViagensForm
from transportes.instrumentation import TranspApiCallTimer
from transportes.models import FiltroFavoritoUsuario, FiltroPadraoTela
from transportes.services.lista_viagens_service import (
    SESSION_KEY_LISTA_VIAGENS_FILTROS,
    append_view_mode_to_qs,
    build_filtros_exibicao,
    build_pagination_state,
    filtros_para_querystring,
    formatar_data,
    montar_filtros_lista_viagens,
    show_origin_column,
)
from transportes.services.transportes_metadata_service import (
    FILTRO_CAMPOS_LISTA_VIAGENS,
    build_clientes_transportadoras_maps,
    build_tipos_status_maps,
    fetch_metadata,
)
from transportes.utils.baseline import _payload_metrics
from transportes.utils.filtros import (
    obter_filtros_tela,
    salvar_filtro_favorito,
)
from transportes.utils.atribuir_motorista import obter_contexto_atribuir_motorista

# Re-export para compatibilidade com detalhe_viagem e outros módulos legados.
__all__ = [
    "buscar_motoristas_travels",
    "buscar_travels_list_resume",
    "formatar_data",
    "lista_viagens",
]

from transportes.views.views_transportes.view_lista_viagens_legacy import (  # noqa: E402
    buscar_motoristas_travels,
    buscar_travels_list_resume,
)


def _resolve_view_mode(request):
    mode = (request.GET.get("view_mode") or "cards").strip().lower()
    return "table" if mode == "table" else "cards"


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def lista_viagens(request):
    titulo = "Lista de Viagens"
    chave_tela = FiltroFavoritoUsuario.TELA_LISTA_VIAGENS
    view_mode = _resolve_view_mode(request)

    modal_session = request.session.pop("lista_viagens_modal_eventos", None) or {}
    modal_travel_event = bool(modal_session)
    selected_travel_ids = modal_session.get("selected_travel_ids", [])
    travel_event_types = modal_session.get("travel_event_types", [])

    with TranspApiCallTimer(
        request,
        phase="metadata",
        url="metadata (parallel)",
    ) as metadata_timer:
        metadata = fetch_metadata()
        resp = metadata["clientes_status"]
        resp_transportadora = metadata["carriers_list"]
        size_clientes, _ = _payload_metrics(resp)
        size_carriers, _ = _payload_metrics(resp_transportadora)
        metadata_timer.payload_size = size_clientes + size_carriers

    maps_ctx = build_tipos_status_maps(resp)
    clientes_map, transportadoras_map = build_clientes_transportadoras_maps(
        resp, resp_transportadora
    )
    maps_ctx["clientes_transportadoras_maps"] = (clientes_map, transportadoras_map)

    filtros = {}

    if request.method == "POST":
        if "limpar_filtros" in request.POST:
            return redirect(f"{request.path}?limpo=1")

        filtros_post = montar_filtros_lista_viagens(request.POST)

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
                chave_tela=chave_tela, ativo=True
            ).first()
            if filtro_padrao and filtro_padrao.filtros:
                filtros = filtro_padrao.filtros
                filtros["Response"] = filtros.get("Response") or "resume"
                request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS] = filtros
                messages.success(request, "Filtro padrão aplicado.")
            else:
                messages.warning(
                    request, "Nenhum filtro padrão cadastrado para esta tela."
                )
            return redirect(f"{request.path}?page=1")

        if "enviar_evento" in request.POST:
            request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS] = filtros_post
            messages.success(request, "Consulta realizada com sucesso!")
            return redirect(f"{request.path}?page=1")

        filtros = obter_filtros_tela(request.user, chave_tela) or {}
        filtros["Response"] = filtros.get("Response") or "resume"
    else:
        limpou_tela = request.GET.get("limpo") == "1"
        if limpou_tela:
            filtros = {"Response": "resume"}
            request.session.pop(SESSION_KEY_LISTA_VIAGENS_FILTROS, None)
        elif (
            "page" in request.GET
            and SESSION_KEY_LISTA_VIAGENS_FILTROS in request.session
        ):
            filtros = dict(request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS])
            filtros["Response"] = filtros.get("Response") or "resume"
        else:
            filtros = obter_filtros_tela(request.user, chave_tela) or {}
            filtros["Response"] = filtros.get("Response") or "resume"

    user_designation = None
    user_designation_id = ""
    user_designation_nome = ""
    usuario_eh_arancia_pa = request.user.groups.filter(name="arancia_PA").exists()

    if usuario_eh_arancia_pa:
        user_designation = getattr(
            getattr(request.user, "designacao", None),
            "informacao_adicional",
            None,
        )
        if user_designation is not None:
            user_designation_id = str(getattr(user_designation, "id", "") or "").strip()
            user_designation_nome = str(
                getattr(user_designation, "nome", "") or ""
            ).strip()

        pa_filtro = str(filtros.get("pa_selecionada", "") or "").strip()
        if user_designation_id:
            if pa_filtro and pa_filtro != user_designation_id:
                messages.error(
                    request,
                    "Você só pode consultar viagens da sua própria PA.",
                )
                return redirect("transportes:lista_viagens")
            filtros["pa_selecionada"] = user_designation_id

    initial_data = {}
    for campo in FILTRO_CAMPOS_LISTA_VIAGENS:
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

    if usuario_eh_arancia_pa and user_designation_id and "pa_selecionada" in form.fields:
        form.fields["pa_selecionada"].choices = [
            (user_designation_id, user_designation_nome or user_designation_id)
        ]
        form.fields["pa_selecionada"].initial = user_designation_id
        for attr in ("readonly", "onclick", "onmousedown"):
            form.fields["pa_selecionada"].widget.attrs[attr] = (
                "true" if attr == "readonly" else "return false;"
            )

    cliente_selecionado = str(filtros.get("cliente", "")).strip()
    tipos_servico_selecionados = filtros.get("tipo_servico", [])
    if isinstance(tipos_servico_selecionados, str):
        tipos_servico_selecionados = (
            [tipos_servico_selecionados] if tipos_servico_selecionados else []
        )

    if "tipo_servico" in form.fields:
        tipos_choices = []
        for item in maps_ctx["tipos_por_cliente"].get(cliente_selecionado, []):
            label = item["type"]
            if item["description"] and item["description"] != item["type"]:
                label = f'{item["type"]} - {item["description"]}'
            tipos_choices.append((item["id"], label))
        form.fields["tipo_servico"].choices = tipos_choices

    if "status_list" in form.fields:
        status_choices = []
        status_ids_adicionados = set()
        for tipo_id in tipos_servico_selecionados:
            for item in maps_ctx["status_por_tipo"].get(str(tipo_id), []):
                if item["id"] in status_ids_adicionados:
                    continue
                status_ids_adicionados.add(item["id"])
                label = item["type"]
                if item["description"] and item["description"] != item["type"]:
                    label = f'{item["type"]} - {item["description"]}'
                status_choices.append((item["id"], label))
        form.fields["status_list"].choices = status_choices

    filtros_ativos = sum(
        1
        for campo in FILTRO_CAMPOS_LISTA_VIAGENS
        if campo != "Response" and filtros.get(campo) not in [None, ""]
    )
    response_mode = filtros.get("Response") or "resume"

    try:
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    page = max(page, 1)

    travels = []
    total = 0
    consultando = bool(filtros_ativos or response_mode)
    async_list_load = consultando

    if consultando:
        request.session[SESSION_KEY_LISTA_VIAGENS_FILTROS] = filtros

    base_qs_no_view = filtros_para_querystring(filtros, FILTRO_CAMPOS_LISTA_VIAGENS)
    pagination = build_pagination_state(page, total, len(travels))
    pagination["base_qs"] = append_view_mode_to_qs(base_qs_no_view, view_mode)

    filtros_exibicao = build_filtros_exibicao(filtros, maps_ctx)
    contexto_atribuir = obter_contexto_atribuir_motorista(request.user)

    return render(
        request,
        "transportes/transportes/lista_viagens.html",
        {
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "lista_viagens",
            "site_title": titulo,
            "form": form,
            "travels": travels,
            "pagination": pagination,
            "filtros_ativos": filtros_ativos,
            "filtros": filtros,
            "filtros_exibicao": filtros_exibicao,
            "tipos_por_cliente": maps_ctx["tipos_por_cliente"],
            "status_por_tipo": maps_ctx["status_por_tipo"],
            "modal_travel_event": modal_travel_event,
            "selected_travel_ids": selected_travel_ids,
            "travel_event_types": travel_event_types,
            "response_mode": response_mode,
            "carriers": resp_transportadora,
            "show_origin_column": show_origin_column(travels),
            "view_mode": view_mode,
            "consultando": consultando,
            "async_list_load": async_list_load,
            "base_qs_no_view": base_qs_no_view,
            "lista_viagens_js_config": {
                "filtros_ativos": filtros_ativos,
                "async_list_load": async_list_load,
                "pode_escolher_transportadora": contexto_atribuir.get(
                    "pode_escolher_transportadora", False
                ),
                "pa_travada": contexto_atribuir.get("pa_travada", False),
                "urls": {
                    "buscar_motoristas": reverse("transportes:buscar_motoristas_travels"),
                    "imprimir_os": reverse("transportes:imprimir_os_viagens"),
                    "list_results": reverse("transportes:api_lista_viagens_list"),
                    "travel_events_template": reverse(
                        "transportes:api_travel_events", kwargs={"travel_id": 0}
                    ),
                },
            },
            **contexto_atribuir,
        },
    )
