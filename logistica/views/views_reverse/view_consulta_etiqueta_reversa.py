from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.urls import reverse

from logistica.forms import ConsultaEtiquetaReversaForm
from logistica.views.views_reverse.view_print_etiqueta_reversa import (
    _buscar_romaneio,
    _location_id_from_user,
)


def _montar_linhas_volumes(request, numero_rom: str, qtde_vol: int) -> list[dict]:
    linhas = []
    for volume in range(1, qtde_vol + 1):
        url_base = reverse(
            "logistica:print_etiqueta_reversa",
            args=[numero_rom, volume],
        )
        linhas.append(
            {
                "volume": volume,
                "url_abrir": url_base,
                "url_imprimir": f"{url_base}?auto=1",
            }
        )
    return linhas


def _volumes_api(romaneio_data: dict) -> int:
    volums = romaneio_data.get("volums") or []
    if not isinstance(volums, list):
        return 0
    return len(volums)


@login_required(login_url="logistica:login")
@permission_required("logistica.lastmile_b2c", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def consulta_etiqueta_reversa(request):
    titulo = "Etiquetas de Reversa"
    volumes = []
    numero_rom = ""
    qtde_vol = None
    url_todos = None

    if request.method == "POST":
        form = ConsultaEtiquetaReversaForm(request.POST, nome_form=titulo)
        if form.is_valid():
            numero_rom = form.cleaned_data["numero_rom"]
            qtde_vol = form.cleaned_data["qtde_vol"]
            location_id = _location_id_from_user(request.user)

            try:
                romaneio_data = _buscar_romaneio(numero_rom, location_id)
            except Exception as exc:
                messages.error(request, f"Erro ao consultar romaneio: {exc}")
                romaneio_data = None

            if not isinstance(romaneio_data, dict) or romaneio_data.get("detail"):
                detail = (romaneio_data or {}).get("detail", "Romaneio não encontrado.")
                messages.error(request, detail)
            else:
                volumes_api = _volumes_api(romaneio_data)
                if volumes_api and volumes_api != qtde_vol:
                    messages.warning(
                        request,
                        (
                            f"O romaneio possui {volumes_api} volume(s) na API, "
                            f"mas foram informados {qtde_vol}. "
                            "Os links abaixo seguem a quantidade informada."
                        ),
                    )

                volumes = _montar_linhas_volumes(request, numero_rom, qtde_vol)
                if qtde_vol > 1:
                    url_base = reverse(
                        "logistica:print_etiqueta_reversa",
                        args=[numero_rom, 1],
                    )
                    url_todos = f"{url_base}?todos=1"
    else:
        form = ConsultaEtiquetaReversaForm(nome_form=titulo)

    return render(
        request,
        "logistica/templates_reverse/consulta_etiqueta_reversa.html",
        {
            "form": form,
            "botao_texto": "Consultar",
            "site_title": titulo,
            "numero_rom": numero_rom,
            "qtde_vol": qtde_vol,
            "volumes": volumes,
            "url_todos": url_todos,
            "current_parent_menu": "logistica",
            "current_menu": "lastmile",
            "current_submenu": "reverse",
            "current_subsubmenu": "consulta_etiqueta_reversa",
        },
    )
