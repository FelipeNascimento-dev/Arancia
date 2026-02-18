from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from logistica.models import Group, GroupAditionalInformation, UserDesignation
from setup.local_settings import API_BASE
from utils.request import RequestClient
from ...forms import ConsultaOSPendForm
from datetime import datetime

TOKEN = "123"
PAGE_SIZE = 50


def get_bases_from_arancia_pa():
    bases = []

    try:
        grupo_pai = Group.objects.get(name="arancia_PA")
    except Group.DoesNotExist:
        return bases

    gai_list = GroupAditionalInformation.objects.filter(group=grupo_pai)

    for gai in gai_list:
        value = f"PA_{gai.cod_iata}"
        label = gai.nome or gai.cod_iata

        bases.append((value, label))

    return sorted(bases, key=lambda x: x[1])


def usuario_pode_ver_todas_bases(user):
    return user.has_perm("transportes.controle_chamados")


def get_base_usuario(user):
    try:
        ud = user.designacao

        if ud and ud.informacao_adicional:
            gai = ud.informacao_adicional

            return {
                "value": f"PA_{gai.cod_iata}",
                "label": gai.nome
            }

        return None

    except Exception:
        return None


@csrf_protect
@login_required(login_url='logistica:login')
def consulta_os_pend(request):
    titulo = 'Consulta de OS Pendentes'
    bases = get_bases_from_arancia_pa()
    pode_ver_todas = usuario_pode_ver_todas_bases(request.user)
    base_usuario = get_base_usuario(request.user)
    tecnicos_choices = []
    itens = []
    page = 1
    has_next = False
    has_prev = False

    base_usuario_data = get_base_usuario(request.user)

    if base_usuario_data:
        base_usuario_value = base_usuario_data["value"]
        base_usuario_label = base_usuario_data["label"]
    else:
        base_usuario_value = None
        base_usuario_label = None

    if request.method == "POST":
        base_selecionada = request.POST.get("base")

        page = int(request.POST.get("page", 1))
        offset = (page - 1) * PAGE_SIZE

        if base_selecionada:
            try:
                url = f"{API_BASE}/v3/controle_campo/tecnicos/{base_selecionada}"

                headers = {
                    "accept": "application/json",
                    "access_token": TOKEN,
                    "Content-Type": "application/json",
                }

                client = RequestClient(
                    method="get",
                    url=url,
                    headers=headers,
                )

                resp = client.send_api_request()

                if isinstance(resp, list):
                    tecnicos_choices = [("", "Todos os Técnicos")] + [
                        (tec["uid"], tec["name"])
                        for tec in resp
                    ]
                else:
                    messages.error(request, "Nenhum técnico retornado.")

            except Exception as e:
                messages.error(request, f"Erro ao buscar técnicos: {e}")

        form = ConsultaOSPendForm(request.POST, nome_form=titulo)
        if pode_ver_todas:
            form.fields["base"].choices = [("", "Selecione a base")] + bases
        else:
            if base_usuario:
                form.fields["base"].choices = [
                    ("", "Selecione a base"),
                    (base_usuario_value, base_usuario_label),
                ]
            else:
                form.fields["base"].choices = [("", "Selecione a base")]
        form.fields["tecnico"].choices = tecnicos_choices

        if not tecnicos_choices:
            messages.warning(
                request,
                "Essa base não possui técnicos cadastrados."
            )

        if "exportar" in request.POST:
            if pode_ver_todas:
                base = request.POST.get("base")
            else:
                base = base_usuario_value
            tecnico_uid = request.POST.get("tecnico")
            tecnico_uid = f'&uid={tecnico_uid}' if tecnico_uid not in (
                '', 'None') else ''
            tag = request.POST.get("tag") or "Pendente"
            data_inicial = request.POST.get("data_inicial")
            data_inicial = f'&data_inicial={data_inicial}' if data_inicial not in (
                '', 'None') else ''
            data_final = request.POST.get("data_final")
            data_final = f'&data_final={data_final}' if data_final not in (
                '', 'None') else ''

            if not base:
                messages.error(request, "Selecione uma base para exportar.")
                return redirect(request.path)

            cod_base = "CTBSEQ"

            params = {
                "unidade": base,
                "uid": tecnico_uid,
                "tag": tag,
                "data_inicial": data_inicial or None,
                "data_final": data_final or None,
            }

            params = {k: v for k, v in params.items() if v}

            # url = f"{API_BASE}/v3/controle_campo/chamados/{cod_base}/export"
            url = f"{API_BASE}/v3/controle_campo/chamados/{cod_base}/export?unidade={base}{tecnico_uid}&tag={tag}{data_inicial}{data_final}"

            return redirect(url)

        if form.is_valid() and "enviar_evento" in request.POST:
            page = int(request.POST.get("page", 1))
            offset = (page - 1) * PAGE_SIZE
            base = form.cleaned_data.get("base")
            tecnico_uid = form.cleaned_data.get("tecnico")
            if not tecnico_uid:
                tecnico_uid = None
            tag = form.cleaned_data.get("tag") or "Pendente"

            data_inicial = form.cleaned_data.get("data_inicial")
            data_final = form.cleaned_data.get("data_final")

            if not data_inicial:
                data_inicial = data_final
            if not data_final:
                data_final = data_inicial

            cod_base = "CTBSEQ"

            if pode_ver_todas:
                base = form.cleaned_data.get("base")
            else:
                base = base_usuario_value

            try:
                url = f"{API_BASE}/v3/controle_campo/chamados/{cod_base}"

                headers = {
                    "accept": "application/json",
                    "access_token": TOKEN,
                    "Content-Type": "application/json",
                }

                params = {
                    "unidade": base,
                    "uid": tecnico_uid,
                    "tag": tag,
                    "data_inicial": data_inicial.strftime("%Y-%m-%d") if data_inicial else None,
                    "data_final": data_final.strftime("%Y-%m-%d") if data_final else None,
                    "offset": offset,
                    "limit": PAGE_SIZE,
                }

                params = {k: v for k, v in params.items() if v is not None}

                client = RequestClient(
                    method="get",
                    url=url,
                    headers=headers,
                    request_data=params,
                )

                resp_chamados = client.send_api_request()

                itens = resp_chamados if isinstance(
                    resp_chamados, list) else []

                for item in itens:
                    if item.get("dt_abertura"):
                        item["dt_abertura_fmt"] = (
                            item["dt_abertura"]
                            .replace("T", " ")
                            .split(".")[0]
                        )
                    else:
                        item["dt_abertura_fmt"] = "-"

                has_next = len(itens) == PAGE_SIZE
                has_prev = page > 1

                messages.success(
                    request,
                    f"Consulta realizada com sucesso. Registros encontrados: {len(resp_chamados) if isinstance(resp_chamados, list) else 0}"
                )

            except Exception as e:
                messages.error(request, f"Erro ao buscar chamados: {e}")

    else:
        form = ConsultaOSPendForm(nome_form=titulo)
        if pode_ver_todas:
            form.fields["base"].choices = [("", "Selecione a base")] + bases
        else:
            if base_usuario:
                form.fields["base"].choices = [
                    ("", "Selecione a base"),
                    (base_usuario_value, base_usuario_label),
                ]
            else:
                form.fields["base"].choices = [("", "Selecione a base")]
        form.fields["tecnico"].choices = []

    return render(
        request,
        'transportes/controle_chamados/consulta_os_pend.html',
        {
            "form": form,
            "itens": itens,
            "page": page,
            "has_next": has_next,
            "has_prev": has_prev,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_campo",
            "current_submenu": "controle_chamados",
            "current_subsubmenu": "consulta_os_pend",
        },
    )
