from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from logistica.models import GroupAditionalInformation, Group
from ...forms import FormCriarOsTransp
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.http import JsonResponse


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


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('transportes.transportes', raise_exception=True)
def criar_os_transp(request):
    titulo = "Criação de OS"

    grupos_base = Group.objects.filter(
        Q(name="arancia_PA") |
        Q(name="arancia_CD") |
        Q(name="arancia_CUSTOMER")
    )

    grupos = GroupAditionalInformation.objects.filter(
        group__in=grupos_base
    ).select_related("group").order_by("nome")

    url_status = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    client = RequestClient(
        method="get",
        url=url_status,
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
    )
    resp = client.send_api_request()

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp["detail"])
        resp = []

    form = FormCriarOsTransp(
        request.GET if request.method == "GET" else request.POST,
        nome_form=titulo,
        payload=resp,
        grupos=grupos
    )

    if request.method == 'POST':

        extra_information = {}

        keys = request.POST.getlist("extra_key[]")
        values = request.POST.getlist("extra_value[]")

        for k, v in zip(keys, values):
            if k:
                extra_information[k] = v

        if "enviar_evento" in request.POST:
            try:
                payload = {
                    "external_order_number": request.POST.get("ex_order_number"),
                    "created_by": request.user.username,
                    "client_id": request.POST.get("cliente"),
                    "origin_id": request.POST.get("origem"),
                    "destination_id": request.POST.get("destino"),
                    "order_type_id": request.POST.get("tipo_os"),
                }

                status_os = request.POST.get("status_os")

                if status_os:
                    payload["order_state_id"] = status_os

                if extra_information:
                    payload["extra_information"] = extra_information

                print(payload)

                url = f"{TRANSP_API_URL}/service_orders/Abertura"
                client = RequestClient(
                    url=url,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    request_data=payload,
                )
                result = client.send_api_request()

                order_number = result.get("service_order").get("order_number")

                if 'detail' in result:
                    messages.error(request, result['detail'])
                else:
                    messages.success(request, "OS criada com sucesso!")
                    return redirect('transportes:detalhe_os_transp', order_number=order_number)

            except:
                messages.error(
                    request, result['detail'] if isinstance(result, dict) and 'detail' in result else "Erro ao criar OS.")
                return redirect('transportes:criar_os_transp')

    form.errors.pop("numero_os", None)
    form.errors.pop("ex_order_number", None)
    form.errors.pop("cliente", None)
    form.errors.pop("origem", None)
    form.errors.pop("destino", None)
    form.errors.pop("tipo_os", None)
    form.errors.pop("status_os", None)

    return render(request, 'transportes/transportes/criar_os.html', {
        "site_title": titulo,
        "form": form,
        "botao_texto": "Criar OS",
        "current_parent_menu": "transportes",
        "current_menu": "lista_os",
    })
