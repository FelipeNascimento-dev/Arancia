from django.shortcuts import render, redirect
from ...forms import ListaTecnicoForm
from logistica.models import Group, GroupAditionalInformation
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib import messages

TOKEN = "123"
PAGE_SIZE = 25


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


def lista_tecnicos(request):
    titulo = 'Lista de Técnicos'
    bases = get_bases_from_arancia_pa()
    tecnicos = []
    page = int(request.POST.get("page", 1))
    offset = (page - 1) * PAGE_SIZE
    has_next = False
    has_prev = page > 1

    form = ListaTecnicoForm(request.POST, nome_form=titulo)
    form.fields["base"].choices = [("", "Selecione a base")] + bases

    if request.method == "POST" and "extrair_tec" in request.POST:
        unidade = request.POST.get("base")

        url_exportar = f"{API_BASE}/v3/controle_campo/tecnicos/{unidade}/export"

        return redirect(url_exportar)

    if request.method == 'POST' and "enviar_evento" in request.POST:
        unidade = request.POST.get("base")

        if not unidade:
            messages.error(request, "Selecione uma base.")
        else:
            url = f"{API_BASE}/v3/controle_campo/tecnicos/{unidade}?offset={offset}&limit={PAGE_SIZE}"
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

            tecnicos = resp if isinstance(resp, list) else []

            for t in tecnicos:
                for campo in ["lastlogin", "lastopening"]:
                    valor = t.get(campo)
                    if valor:
                        t[f"{campo}_fmt"] = valor.replace(
                            "T", " ").split(".")[0]
                    else:
                        t[f"{campo}_fmt"] = "—"

            has_next = len(tecnicos) == PAGE_SIZE

            messages.success(
                request,
                f"Consulta realizada com sucesso. Registros encontrados: {len(resp) if isinstance(resp, list) else 0}"
            )

    form.errors.pop("base", None)

    return render(
        request,
        'transportes/controle_chamados/lista_tecnicos.html', {
            "form": form,
            "tecnicos": tecnicos,
            "page": page,
            "has_next": has_next,
            "has_prev": has_prev,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_chamados",
            "current_submenu": "lista_tecnicos",
        },
    )
