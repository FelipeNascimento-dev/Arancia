from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from logistica.models import GroupAditionalInformation, Group
from ...forms import FormCriarOsTransp
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient


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
        if "enviar_evento" in request.POST:
            try:
                payload = {
                    "external_order_number": request.POST.get("ex_order_number"),
                    "created_by": request.user.username,
                    "client_id": request.POST.get("cliente"),
                    "origin_id": request.POST.get("origem"),
                    "destination_id": request.POST.get("destino"),
                    "order_type_id": request.POST.get("tipo_os"),
                    "order_state_id": request.POST.get("status_os"),
                    "extra_information": {},
                }

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
                    request, "Erro ao criar OS. Verifique os dados e tente novamente.")
                return redirect('transportes:criar_os')

    form.errors.pop("numero_os", None)
    form.errors.pop("ex_order_number", None)
    form.errors.pop("cliente", None)
    form.errors.pop("origem", None)
    form.errors.pop("destino", None)
    form.errors.pop("tipo_os", None)
    form.errors.pop("status_os", None)

    return render(request, 'transportes/transportes/criar_os.html', {
        'site_title': titulo,
        'form': form,
        'botao_texto': 'Criar OS',

    })
