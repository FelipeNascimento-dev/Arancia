from ..forms import ClientCheckInForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from ..models import GroupAditionalInformation, UserDesignation
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
import json


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def client_checkin(request):
    client_data = request.session.get("selected_client", {})
    client_name = client_data.get("client_name", "Cliente não selecionado")
    titulo = f"Check-In {client_name}"

    pedido_atrelado = request.session.get("order", "")

    product_choices = []
    try:
        if client_name:
            url_products = f"{STOCK_API_URL}/v1/products/{client_name.lower()}"
            res = RequestClient(
                url=url_products,
                method="GET",
                headers={"Accept": "application/json"}
            )
            result = res.send_api_request()

            try:
                if isinstance(result, (dict, list)):
                    data = result
                elif isinstance(result, (str, bytes)):
                    data = json.loads(result)
                elif hasattr(result, "json"):
                    data = result.json()
                elif hasattr(result, "text"):
                    data = json.loads(result.text)
                else:
                    data = []
            except Exception:
                data = []

            if isinstance(data, list) and len(data) > 0:
                product_choices = []
                product_map = {}

                for p in data:
                    product_id = p.get("id") or 0
                    sku = p.get("sku") or p.get("product_code") or ""
                    desc = p.get("description") or p.get(
                        "product_name") or "Sem descrição"
                    display = f"{sku} - {desc}".strip(" -")

                    product_choices.append((str(product_id), display))
                    product_map[str(product_id)] = {
                        "sku": sku,
                        "desc": desc,
                        "id": product_id,
                    }

                request.session["product_map"] = product_map
            else:
                product_choices = [("", "Nenhum produto encontrado")]
        else:
            product_choices = [("", "Cliente não selecionado")]
    except Exception as e:
        messages.error(request, f"Erro ao obter produtos: {e}")
        product_choices = [("", "Erro ao carregar produtos")]

    try:
        grupos = GroupAditionalInformation.objects.filter(
            group__name__iregex=r'arancia_(PA|CD)'
        ).select_related("group").order_by("group__name")

        from_choices = [
            (str(g.group.id),
             f"{g.group.name} - {g.nome or g.razao_social or 'Sem nome'}")
            for g in grupos
        ]
        if not from_choices:
            from_choices = [("", "Nenhum PA/CD encontrado")]
    except Exception as e:
        messages.error(request, f"Erro ao carregar grupos: {e}")
        from_choices = [("", "Erro ao carregar origens")]

    to_location_value = ""
    try:
        user_designacao = UserDesignation.objects.filter(user=request.user).select_related(
            "informacao_adicional", "informacao_adicional__group"
        ).first()

        if user_designacao and user_designacao.informacao_adicional:
            group_info = user_designacao.informacao_adicional

    except Exception as e:
        messages.error(request, f"Erro ao identificar destino do usuário: {e}")

    except Exception as e:
        messages.error(request, f"Erro ao identificar destino do usuário: {e}")

    if request.method == "POST":
        to_location_id = str(request.session.get("to_location_id", ""))
        to_location_label = ""
        if isinstance(to_location_value, dict):
            to_location_label = to_location_value.get("label", "")
        elif to_location_id:
            to_location_label = f"Destino {to_location_id}"

        form = ClientCheckInForm(
            request.POST,
            nome_form=titulo,
            from_choices=from_choices,
            product_choices=product_choices,
        )

        form.fields["to_location"].choices = [
            (to_location_id, to_location_label)
        ]
        form.fields["to_location"].initial = to_location_id

        if form.is_valid():
            try:
                product_id = int(form.cleaned_data.get("product"))
                from_location_id = int(
                    form.cleaned_data.get("from_location") or 0)
                to_location_id = group_info.id

                payload = {
                    "item": {
                        "product_id": product_id,
                        "serial": form.cleaned_data.get("serial"),
                        "extra_info": {}
                    },
                    "client_name": client_name.lower(),
                    "movement_type": "IN",
                    "from_location_id": from_location_id,
                    "to_location_id": to_location_id,
                    "order_origin_id": 3,
                    "order_number": form.cleaned_data.get("pedido_atrelado") or form.cleaned_data.get("pedido"),
                    "volume_number": form.cleaned_data.get("volume") or 1,
                    "kit_number": f"KIT-{form.cleaned_data.get('kit') or 1}",
                    "created_by": request.user.username.upper(),
                }

                print(payload)

                url_mov = f"{STOCK_API_URL}/v1/movements/"
                res = RequestClient(
                    url=url_mov,
                    method="POST",
                    headers={"Accept": "application/json",
                             "Content-Type": "application/json"},
                    request_data=payload
                ).send_api_request()

                if isinstance(res, dict) and (res.get("id") or "success" in str(res).lower()):
                    messages.success(
                        request, "Movimento registrado com sucesso!")
                else:
                    messages.error(
                        request, f"Falha ao registrar movimento: {res}")

            except Exception as e:
                messages.error(request, f"Erro ao enviar movimento: {e}")
    else:
        initial_data = {
            "pedido_atrelado": pedido_atrelado,
            "to_location": to_location_value.get("label", "") if isinstance(to_location_value, dict) else "",
        }

        form = ClientCheckInForm(
            nome_form=titulo,
            initial=initial_data,
            from_choices=from_choices,
            product_choices=product_choices,
        )

        if isinstance(to_location_value, dict):
            form.fields["to_location"].choices = [
                (str(to_location_value["id"]), to_location_value["label"])
            ]
            form.fields["to_location"].initial = str(to_location_value["id"])
            request.session["to_location_id"] = to_location_value["id"]
        else:
            form.fields["to_location"].choices = [
                ("", "Destino não identificado")]
            request.session["to_location_id"] = 0

    return render(
        request,
        "logistica/client_checkin.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Registrar Check-In",
        },
    )
