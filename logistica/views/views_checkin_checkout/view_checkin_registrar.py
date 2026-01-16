from ...forms import ClientCheckInForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from ...models import GroupAditionalInformation, UserDesignation
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
import json


@login_required(login_url='logistica:login')
@permission_required('logistica.checkin_principal', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def client_checkin(request):
    CHECKLIST_CLARO = [
        "CONTROLE",
        "CABO HDMI",
        "CABO A/V",
        "CABO DE REDE",
        "CABO DE FORÇA",
        "FONTE",
        "FONTE PADRÃO",
        "MINI ISOLADOR",
        "HD DIGITAL",
        "DEC DIGITAL",
        "DEC PHILIPS",
        "EMTA/MODEM",
        "MESH",
        "BOX",
    ]

    client_name = request.GET.get("client")
    selected_client = request.session.get("selected_client", {})

    client_code = selected_client.get("client_code")
    client_name = request.GET.get(
        "client") or selected_client.get("client_name")

    if not client_name:
        client_name = request.session.get(
            "selected_client", {}).get("client_name")

    if not client_name:
        client_name = "Cliente não selecionado"

    titulo = f"Check-In {client_name}"

    pedido_atrelado = request.GET.get("pedido") or request.session.get(
        "pedido") or request.session.get("order", "")

    is_claro = client_code == "claro"

    product_choices = []
    try:
        if client_name:
            url_products = f"{STOCK_API_URL}/v1/products/{client_code.lower()}"
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

    to_location_choices = []
    to_location_initial = None
    to_location_disabled = False

    try:
        if request.user.has_perm('logistica.gestao_total'):
            destinos = (
                GroupAditionalInformation.objects
                .select_related("group")
                .filter(group__name__iregex=r"arancia_(PA|CD)")
                .order_by("group__name", "nome")
            )

            for gi in destinos:
                prefix = "[PA]" if gi.group.name == "arancia_PA" else "[CD]"
                label = f"{prefix} {gi.nome or gi.razao_social or 'Sem nome'}"

                to_location_choices.append((str(gi.id), label))

        else:
            user_designacao = (
                UserDesignation.objects
                .select_related("informacao_adicional", "informacao_adicional__group")
                .filter(user=request.user)
                .first()
            )

            if user_designacao and user_designacao.informacao_adicional:
                gi = user_designacao.informacao_adicional
                prefix = "[PA]" if gi.group.name == "arancia_PA" else "[CD]"
                label = f"{prefix} {gi.nome or gi.razao_social or 'Sem nome'}"

                to_location_choices = [(str(gi.id), label)]
                to_location_initial = str(gi.id)
                to_location_disabled = True

    except Exception as e:
        messages.error(request, f"Erro ao identificar destino do usuário: {e}")

    if request.method == "POST" and "gerar_serial_provisorio" in request.POST:
        form = ClientCheckInForm(
            request.POST,
            nome_form=titulo,
            from_choices=from_choices,
            product_choices=product_choices,
        )

        old_serial = request.POST.get("old_serial")
        reason = request.POST.get("reason")

        payload = {
            "old_serial_number": old_serial if old_serial else None,
            "reason": reason if reason else "Não Informado",
            "created_by": request.user.username,
        }

        try:
            res = RequestClient(
                url=f"{STOCK_API_URL}/v1/item/provisional/",
                method="POST",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                request_data=payload
            )
            api_result = res.send_api_request()

            new_serial = (
                api_result.get("serial")
                or api_result.get("new_serial_number")
                or ""
            )
            print(new_serial)

            messages.success(
                request,
                f"Serial provisório gerado com sucesso: {new_serial}"
            )

            form = ClientCheckInForm(
                nome_form=titulo,
                from_choices=from_choices,
                product_choices=product_choices,
                initial={
                    "serial": new_serial
                }
            )

            form.fields["to_location"].choices = [
                ("", "")] + to_location_choices
            form.fields["to_location"].initial = to_location_initial
            form.fields["to_location"].disabled = to_location_disabled

            print_url = reverse(
                "logistica:print_serial",
                args=[new_serial]
            )

            request.session["print_serial_url"] = print_url

            return render(
                request,
                "logistica/templates_checkin_checkout/checkin_registrar.html",
                {
                    "form": form,
                    "site_title": titulo,
                    "botao_texto": "Registrar Check-In",
                    "is_claro": is_claro,
                    "checklist_claro": CHECKLIST_CLARO,
                    "print_serial_url": print_url,
                },
            )

        except Exception as e:
            messages.error(request, f"Erro ao gerar serial provisório: {e}")
            api_result = None

    elif request.method == "POST":
        form = ClientCheckInForm(
            request.POST,
            nome_form=titulo,
            from_choices=from_choices,
            product_choices=product_choices,
        )

        form.fields["to_location"].choices = [("", "")] + to_location_choices
        form.fields["to_location"].initial = to_location_initial
        form.fields["to_location"].disabled = to_location_disabled

        if form.is_valid():
            request.session["checkin_form_data"] = {
                "product": form.cleaned_data.get("product"),
                "from_location": form.cleaned_data.get("from_location"),
                "pedido_atrelado": form.cleaned_data.get("pedido_atrelado"),
                "pedido": form.cleaned_data.get("pedido"),
                "volume": form.cleaned_data.get("volume"),
                "kit": form.cleaned_data.get("kit"),
            }

            try:
                product_id = int(form.cleaned_data["product"])
                from_location_id = int(
                    form.cleaned_data.get("from_location") or 0)
                to_location_id = int(form.cleaned_data["to_location"])

                order_number = form.cleaned_data.get("pedido_atrelado")
                romaneio_number = form.cleaned_data.get("pedido")

                extra_info_root = (
                    {"romaneio_number": romaneio_number}
                    if romaneio_number else {}
                )

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
                    "order_number": order_number,
                    "volume_number": form.cleaned_data.get("volume") or 1,
                    "kit_number": f"KIT-{form.cleaned_data.get('kit') or 1}",
                    "extra_info": extra_info_root,
                    "created_by": request.user.username.upper(),
                }

                res = RequestClient(
                    url=f"{STOCK_API_URL}/v1/movements/",
                    method="POST",
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    request_data=payload
                ).send_api_request()

                if isinstance(res, dict) and (res.get("id") or "success" in str(res).lower()):
                    messages.success(
                        request, "Movimento registrado com sucesso!")
                    return redirect(reverse("logistica:client_checkin"))
                else:
                    messages.error(
                        request, f"Falha ao registrar movimento: {res}")

            except Exception as e:
                messages.error(request, f"Erro ao enviar movimento: {e}")

    else:
        saved = request.session.pop("checkin_form_data", {})

        initial_data = {
            "product": saved.get("product", ""),
            "from_location": saved.get("from_location", ""),
            "pedido_atrelado": saved.get("pedido_atrelado") or pedido_atrelado,
            "pedido": saved.get("pedido", ""),
            "volume": saved.get("volume", "1"),
            "kit": saved.get("kit", "1"),
            "serial": "",
            "to_location": to_location_initial,
        }

        form = ClientCheckInForm(
            nome_form=titulo,
            initial=initial_data,
            from_choices=from_choices,
            product_choices=product_choices,
        )

        form.fields["to_location"].choices = [("", "")] + to_location_choices
        form.fields["to_location"].initial = to_location_initial
        form.fields["to_location"].disabled = to_location_disabled

    return render(
        request,
        "logistica/templates_checkin_checkout/checkin_registrar.html",
        {
            "form": form,
            "site_title": titulo,
            "is_claro": is_claro,
            "checklist_claro": CHECKLIST_CLARO,
            "botao_texto": "Registrar Check-In",
        },
    )
