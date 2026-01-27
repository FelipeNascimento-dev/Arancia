from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from logistica.models import Group, GroupAditionalInformation
from setup.local_settings import API_BASE
from utils.request import RequestClient
from ...forms import ConsultaOSForm
from datetime import datetime

TOKEN = "123"


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


@csrf_protect
@login_required(login_url='logistica:login')
def consulta_os(request):
    titulo = 'Consulta de OS'

    bases = get_bases_from_arancia_pa()

    tecnicos_choices = []

    itens = []

    if request.method == "POST":
        base_selecionada = request.POST.get("base")

        if base_selecionada:
            try:
                url = f"{API_BASE}/v3/controle_campo/tecnicos/{base_selecionada}?offset=0&limit=100"

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

        form = ConsultaOSForm(request.POST, nome_form=titulo)
        form.fields["base"].choices = bases
        form.fields["tecnico"].choices = tecnicos_choices

        if not tecnicos_choices:
            messages.warning(
                request,
                "Essa base não possui técnicos cadastrados."
            )

        if form.is_valid() and "enviar_evento" in request.POST:
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
                    "offset": 0,
                    "limit": 100,
                }

                params = {k: v for k, v in params.items() if v is not None}

                client = RequestClient(
                    method="get",
                    url=url,
                    headers=headers,
                    request_data=params,
                )

                resp_chamados = client.send_api_request()

                for item in itens:
                    if item.get("dt_abertura"):
                        item["dt_abertura_fmt"] = (
                            item["dt_abertura"]
                            .replace("T", " ")
                            .split(".")[0]
                        )
                    else:
                        item["dt_abertura_fmt"] = "-"

                itens = resp_chamados if isinstance(
                    resp_chamados, list) else []

                messages.success(
                    request,
                    f"Consulta realizada com sucesso. Registros encontrados: {len(resp_chamados) if isinstance(resp_chamados, list) else 0}"
                )

            except Exception as e:
                messages.error(request, f"Erro ao buscar chamados: {e}")

        elif "exportar_tec" in request.POST:
            url = f"{API_BASE}/v3/controle_campo/chamados/{base}/export"

            client = RequestClient(
                method="get",
                url=url,
                headers=headers,
                request_data=params,
            )

            export_resp = client.send_api_request()

            return export_resp

        form.errors.pop("tecnico", None)

    else:
        form = ConsultaOSForm(nome_form=titulo)
        form.fields["base"].choices = bases
        form.fields["tecnico"].choices = []

    return render(
        request,
        'transportes/controle_chamados/consulta_os.html',
        {
            "form": form,
            "itens": itens,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_chamados",
            "current_submenu": "consulta_os",
        },
    )
