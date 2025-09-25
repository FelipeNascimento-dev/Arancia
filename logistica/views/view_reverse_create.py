from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import datetime
from ..forms import ReverseCreateForm
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL

JSON_CT = "application/json"


def reverse_create(request):
    titulo = 'Reversa de Equipamento'
    result = request.session.get('result', None)
    romaneio_in = request.session.get("romaneio_num", None)

    result = request.session.get("result", None)

    user = request.user
    sales_channel = user.designacao.informacao_adicional.sales_channel
    if sales_channel == 'all':
        location_id = 0
    else:
        location_id = user.designacao.informacao_adicional_id

    user_sales_channel = None
    try:
        if (
            request.user.is_authenticated
            and hasattr(request.user, "designacao")
            and request.user.designacao.informacao_adicional
        ):
            user_sales_channel = (
                request.user.designacao.informacao_adicional.sales_channel or ""
            ).strip()
    except Exception:
        user_sales_channel = None

    form = ReverseCreateForm(
        request.POST or None,
        nome_form=titulo,
        user_sales_channel=user_sales_channel,
        romaneio_num=romaneio_in,
    )

    if "volums" not in request.session:
        request.session["volums"] = []

    volums = request.session["volums"]

    if request.method == "POST" and form.is_valid():
        serial = form.cleaned_data.get("serial")

        if serial:
            if len(volums) == 0:
                volums.append({"volum_number": 1, "kits": []})

            ultimo_volume = volums[-1]

            if len(ultimo_volume["kits"]) >= 10:
                if len(volums) >= 25:
                    messages.error(
                        request, "Limite máximo de 25 volumes atingido!")
                    return redirect("logistica:reverse_create")
                else:
                    novo_numero = int(ultimo_volume["volum_number"]) + 1
                    volums.append({"volum_number": novo_numero, "kits": []})
                    ultimo_volume = volums[-1]

            kit_number = len(ultimo_volume["kits"]) + 1

            ultimo_volume["kits"].append({
                "kit_number": kit_number,
                "serial": serial,
                "order_number": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "created_by": request.user.username if request.user.is_authenticated else "SYSTEM",
                "created_at": datetime.now().isoformat()
            })

            request.session["volums"] = volums
            request.session.modified = True

            payload = {
                "serial": serial,
                "volume_number": str(ultimo_volume["volum_number"]),
                "kit_number": str(kit_number),
                "client": "cielo",
                "location_id": location_id,
                "create_by": request.user.username if request.user.is_authenticated else "SYSTEM"
            }

            url = f"{STOCK_API_URL}/v1/romaneios/insert-items/{romaneio_in}"

            client = RequestClient(
                url=url,
                method="POST",
                headers={"Accept": JSON_CT,
                         "Content-Type": "application/json"},
                request_data=payload,
            )
            print(payload)

            result = client.send_api_request()

            if isinstance(result, dict) and "detail" in result:
                messages.error(request, f"Erro API: {result}")
            else:
                request.session["result"] = result
                request.session.modified = True
                messages.success(
                    request, f"Serial {serial} inserido no romaneio!")

            if int(ultimo_volume["volum_number"]) == 25 and len(ultimo_volume["kits"]) == 10:
                messages.warning(
                    request,
                    "Você atingiu o limite de 25 volumes com 10 kits cada!"
                )

            return redirect("logistica:reverse_create")

    context = {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "result": result,
    }
    return render(request, "logistica/reverse_create.html", context)


def delete_btn(request, serial):
    romaneio_in = request.session.get("romaneio_num", None)

    if not romaneio_in:
        messages.error(request, "Romaneio não encontrado na sessão.")
        return redirect("logistica:reverse_create")

    url = f"{STOCK_API_URL}/v1/romaneios/{romaneio_in}/?serial={serial}"

    client = RequestClient(
        url=url,
        method="DELETE",
        headers={"Accept": JSON_CT, "Content-Type": "application/json"},
    )

    result = client.send_api_request()

    if isinstance(result, dict) and "detail" in result:
        messages.error(request, f"Erro ao deletar: {result['detail']}")
    else:
        messages.success(request, f"Serial {serial} removido com sucesso!")

    return redirect("logistica:reverse_create")
# 6C671351 TESTEDAVI
